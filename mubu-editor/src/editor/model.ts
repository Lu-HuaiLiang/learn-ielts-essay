import { Fragment, Node as PMNode, Schema } from "prosemirror-model";
import {
  Command,
  EditorState,
  TextSelection,
  Transaction,
} from "prosemirror-state";
import { closeHistory } from "prosemirror-history";

export const uid = () => crypto.randomUUID();
export function safeLink(value: string) {
  const href = value.trim();
  return /^(https?:\/\/|mailto:|#)/i.test(href) ? href : "";
}
export const schema = new Schema({
  nodes: {
    doc: { content: "title outlineItem+" },
    title: {
      content: "inline*",
      marks: "",
      toDOM: () => [
        "h1",
        { class: "document-title", "data-placeholder": "无标题文档" },
        0,
      ],
      parseDOM: [{ tag: "h1.document-title" }],
    },
    outlineItem: {
      content: "body description? outlineItem*",
      attrs: { id: { default: "" }, level: { default: 0 } },
      defining: true,
      toDOM: (n) => [
        "div",
        { "data-outline": n.attrs.id, "data-level": n.attrs.level },
        0,
      ],
      parseDOM: [
        {
          tag: "div[data-outline]",
          getAttrs: (el) => ({
            id: (el as HTMLElement).dataset.outline || uid(),
            level: Number((el as HTMLElement).dataset.level) || 0,
          }),
        },
      ],
    },
    body: {
      content: "inline*",
      toDOM: () => [
        "div",
        { class: "node-body", "data-placeholder": "输入内容" },
        0,
      ],
      parseDOM: [{ tag: ".node-body" }, { tag: "p" }],
    },
    description: {
      content: "inline*",
      toDOM: () => [
        "div",
        { class: "node-description", "data-placeholder": "添加描述…" },
        0,
      ],
      parseDOM: [{ tag: ".node-description" }],
    },
    text: { group: "inline" },
    hard_break: {
      inline: true,
      group: "inline",
      selectable: false,
      toDOM: () => ["br"],
      parseDOM: [{ tag: "br" }],
    },
  },
  marks: {
    bold: {
      toDOM: () => ["strong", 0],
      parseDOM: [
        { tag: "strong" },
        { tag: "b" },
        {
          style: "font-weight",
          getAttrs: (v) => (/^(bold|[6-9]00)$/.test(String(v)) ? null : false),
        },
      ],
    },
    italic: {
      toDOM: () => ["em", 0],
      parseDOM: [{ tag: "em" }, { tag: "i" }, { style: "font-style=italic" }],
    },
    underline: {
      toDOM: () => ["u", 0],
      parseDOM: [{ tag: "u" }, { style: "text-decoration=underline" }],
    },
    strike: {
      toDOM: () => ["s", 0],
      parseDOM: [
        { tag: "s" },
        { tag: "del" },
        { style: "text-decoration=line-through" },
      ],
    },
    code: { toDOM: () => ["code", 0], parseDOM: [{ tag: "code" }] },
    color: {
      attrs: { color: {} },
      toDOM: (m) => ["span", { style: `color:${m.attrs.color}` }, 0],
      parseDOM: [{ style: "color", getAttrs: (color) => ({ color }) }],
    },
    highlight: {
      attrs: { color: {} },
      toDOM: (m) => ["mark", { style: `background-color:${m.attrs.color}` }, 0],
      parseDOM: [
        {
          tag: "mark",
          getAttrs: (el) => ({
            color: (el as HTMLElement).style.backgroundColor || "#fff0a8",
          }),
        },
        { style: "background-color", getAttrs: (color) => ({ color }) },
      ],
    },
    link: {
      attrs: { href: {} },
      inclusive: false,
      toDOM: (m) => [
        "a",
        {
          href: safeLink(m.attrs.href),
          target: "_blank",
          rel: "noopener noreferrer",
        },
        0,
      ],
      parseDOM: [
        {
          tag: "a[href]",
          getAttrs: (el) =>
            safeLink((el as HTMLElement).getAttribute("href") || "")
              ? { href: safeLink((el as HTMLElement).getAttribute("href")!) }
              : false,
        },
      ],
    },
  },
});

export function item(
  text = "",
  children: PMNode[] = [],
  id: string = uid(),
  description = "",
): PMNode {
  return schema.nodes.outlineItem.create({ id }, [
    schema.nodes.body.create(null, text ? schema.text(text) : null),
    ...(description
      ? [
          schema.nodes.description.create(
            null,
            Fragment.fromArray(
              description
                .split("\n")
                .flatMap((line, i) => [
                  ...(i ? [schema.nodes.hard_break.create()] : []),
                  ...(line ? [schema.text(line)] : []),
                ]),
            ),
          ),
        ]
      : []),
    ...children,
  ]);
}
export const documentFrom = (title: string, nodes: PMNode[]) =>
  schema.nodes.doc.create(null, [
    schema.nodes.title.create(null, title ? schema.text(title) : null),
    ...(nodes.length ? nodes : [item()]),
  ]);
export interface Entry {
  id: string;
  node: PMNode;
  pos: number;
  depth: number;
  parent: string | null;
  ancestors: string[];
}
export function entries(doc: PMNode): Entry[] {
  const result: Entry[] = [];
  const walk = (
    parent: PMNode,
    base: number,
    depth: number,
    ancestors: string[],
  ) =>
    parent.forEach((node, offset) => {
      if (node.type.name !== "outlineItem") return;
      const pos = base + offset;
      result.push({
        id: node.attrs.id,
        node,
        pos,
        depth,
        parent: ancestors.at(-1) || null,
        ancestors,
      });
      walk(node, pos + 1, depth + 1, [...ancestors, node.attrs.id]);
    });
  walk(doc, 0, 0, []);
  return result;
}
export function currentEntry(state: EditorState) {
  const p = state.selection.$from;
  for (let d = p.depth; d > 0; d--)
    if (p.node(d).type.name === "outlineItem") {
      const id = p.node(d).attrs.id;
      return entries(state.doc).find((e) => e.id === id);
    }
}
export function selectionIds(state: EditorState): string[] {
  if (state.selection.empty) {
    const e = currentEntry(state);
    return e ? [e.id] : [];
  }
  return entries(state.doc)
    .filter(
      (e) =>
        e.pos + 1 < state.selection.to &&
        e.pos + 2 + e.node.child(0).content.size >= state.selection.from,
    )
    .map((e) => e.id);
}
export function topEntries(doc: PMNode, ids: string[]) {
  const set = new Set(ids);
  return entries(doc).filter(
    (e) => set.has(e.id) && !e.ancestors.some((id) => set.has(id)),
  );
}
export function freshIds(node: PMNode): PMNode {
  if (node.isText) return node;
  return node.type.create(
    node.type.name === "outlineItem"
      ? { ...node.attrs, id: uid() }
      : node.attrs,
    Fragment.fromArray(childrenOf(node).map(freshIds)),
    node.marks,
  );
}
export const childrenOf = (node: PMNode) => {
  const children: PMNode[] = [];
  node.forEach((c) => children.push(c));
  return children;
};

interface Tree {
  node: PMNode;
  children: Tree[];
}
const unpack = (node: PMNode): Tree => ({
  node,
  children: childrenOf(node)
    .filter((n) => n.type.name === "outlineItem")
    .map(unpack),
});
const pack = (tree: Tree): PMNode =>
  tree.node.copy(
    Fragment.fromArray([
      ...childrenOf(tree.node).filter((n) => n.type.name !== "outlineItem"),
      ...tree.children.map(pack),
    ]),
  );
function locate(
  roots: Tree[],
  id: string,
): { siblings: Tree[]; index: number; parent: Tree | null } | undefined {
  const walk = (
    list: Tree[],
    parent: Tree | null,
  ): ReturnType<typeof locate> => {
    for (let i = 0; i < list.length; i++) {
      if (list[i].node.attrs.id === id)
        return { siblings: list, index: i, parent };
      const found = walk(list[i].children, list[i]);
      if (found) return found;
    }
  };
  return walk(roots, null);
}
function bookmark(state: EditorState) {
  return {
    id: currentEntry(state)?.id,
    field: state.selection.$from.parent.type.name,
    offset: state.selection.$from.parentOffset,
  };
}
export function textPosition(
  doc: PMNode,
  id: string,
  field = "body",
  offset = 0,
): number | undefined {
  const e = entries(doc).find((e) => e.id === id);
  if (!e) return;
  let result: number | undefined;
  e.node.forEach((n, o) => {
    if (n.type.name === field)
      result = e.pos + 2 + o + Math.min(offset, n.content.size);
  });
  return result;
}
function commitTree(
  state: EditorState,
  dispatch: ((tr: Transaction) => void) | undefined,
  nodes: PMNode[],
  focus = bookmark(state),
) {
  if (!dispatch) return true;
  const tr = closeHistory(state.tr).replaceWith(
    state.doc.firstChild!.nodeSize,
    state.doc.content.size,
    nodes.length ? nodes : [item()],
  );
  let pos = focus.id
    ? textPosition(tr.doc, focus.id, focus.field, focus.offset)
    : undefined;
  pos ??= entries(tr.doc)[0].pos + 2;
  tr.setSelection(TextSelection.create(tr.doc, pos));
  dispatch(closeHistory(tr).scrollIntoView());
  return true;
}
export type TreeAction =
  | "indent"
  | "outdent"
  | "up"
  | "down"
  | "delete"
  | "duplicate"
  | "move"
  | "insert"
  | "replace";
export function editTree(
  action: TreeAction,
  ids: string[],
  options: {
    target?: string;
    placement?: "before" | "after" | "inside";
    nodes?: PMNode[];
  } = {},
): Command {
  return (state, dispatch) => {
    const selected = topEntries(state.doc, ids);
    if (!selected.length) return false;
    const roots = childrenOf(state.doc).slice(1).map(unpack);
    let changed = false;
    let focus = bookmark(state);
    if (action === "move") {
      const targetEntry = entries(state.doc).find(
        (e) => e.id === options.target,
      );
      if (
        !targetEntry ||
        selected.some(
          (e) =>
            e.id === targetEntry.id || targetEntry.ancestors.includes(e.id),
        )
      )
        return false;
      const moved: Tree[] = [];
      for (const e of selected) {
        const loc = locate(roots, e.id)!;
        moved.push(...loc.siblings.splice(loc.index, 1));
      }
      const target = locate(roots, options.target!)!;
      if (options.placement === "inside")
        target.siblings[target.index].children.push(...moved);
      else
        target.siblings.splice(
          target.index + (options.placement === "before" ? 0 : 1),
          0,
          ...moved,
        );
      changed = true;
      focus = { id: selected[0].id, field: "body", offset: 0 };
    } else if (action === "replace") {
      for (const e of selected.slice(1).reverse()) {
        const loc = locate(roots, e.id)!;
        loc.siblings.splice(loc.index, 1);
      }
      const first = locate(roots, selected[0].id)!;
      const nodes = options.nodes || [item()];
      first.siblings.splice(first.index, 1, ...nodes.map(unpack));
      focus = {
        id: nodes[0].attrs.id,
        field: "body",
        offset: nodes[0].firstChild!.content.size,
      };
      changed = true;
    } else if (action === "insert") {
      const loc = locate(roots, selected.at(-1)!.id)!;
      const nodes = options.nodes || [item()];
      loc.siblings.splice(loc.index + 1, 0, ...nodes.map(unpack));
      focus = { id: nodes[0].attrs.id, field: "body", offset: 0 };
      changed = true;
    } else {
      const ordered =
        action === "outdent" || action === "down"
          ? [...selected].reverse()
          : selected;
      for (const e of ordered) {
        const loc = locate(roots, e.id);
        if (!loc) continue;
        const { siblings, index, parent } = loc;
        const tree = siblings[index];
        if (
          action === "indent" &&
          index > 0 &&
          !ids.includes(siblings[index - 1].node.attrs.id)
        ) {
          siblings[index - 1].children.push(...siblings.splice(index, 1));
          changed = true;
        }
        if (action === "outdent" && parent) {
          const p = locate(roots, parent.node.attrs.id)!;
          p.siblings.splice(p.index + 1, 0, ...siblings.splice(index, 1));
          changed = true;
        }
        if (
          action === "up" &&
          index > 0 &&
          !ids.includes(siblings[index - 1].node.attrs.id)
        ) {
          siblings.splice(index - 1, 0, ...siblings.splice(index, 1));
          changed = true;
        }
        if (
          action === "down" &&
          index < siblings.length - 1 &&
          !ids.includes(siblings[index + 1].node.attrs.id)
        ) {
          siblings.splice(index + 1, 0, ...siblings.splice(index, 1));
          changed = true;
        }
        if (action === "delete") {
          siblings.splice(index, 1);
          changed = true;
        }
        if (action === "duplicate") {
          const copy = unpack(freshIds(pack(tree)));
          siblings.splice(index + 1, 0, copy);
          focus = { id: copy.node.attrs.id, field: "body", offset: 0 };
          changed = true;
        }
      }
    }
    return changed
      ? commitTree(state, dispatch, roots.map(pack), focus)
      : false;
  };
}
export const splitItem: Command = (state, dispatch) => {
  const field = state.selection.$from.parent.type.name;
  if (field === "description") {
    if (!dispatch) return true;
    const tr = state.tr.deleteSelection();
    const { $from } = tr.selection;
    let nextPrefix = "";
    if ($from.parent.type.name === "description") {
      const text = $from.parent.textBetween(
        0,
        $from.parent.content.size,
        "",
        "\n",
      );
      const offset = $from.parentOffset;
      const start = text.slice(0, offset).lastIndexOf("\n") + 1;
      const nextBreak = text.indexOf("\n", offset);
      const end = nextBreak < 0 ? text.length : nextBreak;
      const line = text.slice(start, end);
      // Require a separator before content so decimals such as 1.25 stay plain text.
      const numbered = /^([ \t]*)(\d+)\.(?:([ \t\u00a0]+)(.*))?$/.exec(line);
      if (
        numbered &&
        offset - start >= numbered[1].length + numbered[2].length + 1
      ) {
        if (!(numbered[4] || "").replace(/\u200b/g, "").trim()) {
          const from = $from.start() + start;
          tr.delete(from, from + line.length);
          dispatch(tr.scrollIntoView());
          return true;
        }
        nextPrefix = `${numbered[1]}${BigInt(numbered[2]) + 1n}.${numbered[3] || " "}`;
      }
    }
    tr.replaceSelectionWith(schema.nodes.hard_break.create());
    if (nextPrefix) tr.insertText(nextPrefix);
    dispatch(tr.scrollIntoView());
    return true;
  }
  if (field === "title") {
    if (dispatch)
      dispatch(
        state.tr
          .setSelection(
            TextSelection.create(state.doc, entries(state.doc)[0].pos + 2),
          )
          .scrollIntoView(),
      );
    return true;
  }
  if (field !== "body") return false;
  if (!state.selection.empty) {
    if (dispatch) {
      const tr = state.tr.deleteSelection();
      const intermediate = state.apply(tr);
      splitItem(intermediate, (next) => {
        const combined = closeHistory(state.tr);
        tr.steps.forEach((s) => combined.step(s));
        next.steps.forEach((s) => combined.step(s));
        combined.setSelection(next.selection);
        dispatch(closeHistory(combined).scrollIntoView());
      });
    }
    return true;
  }
  const e = currentEntry(state)!;
  if (!e.node.firstChild!.content.size && e.parent)
    return editTree("outdent", [e.id])(state, dispatch);
  const roots = childrenOf(state.doc).slice(1).map(unpack);
  const loc = locate(roots, e.id)!;
  const offset = state.selection.$from.parentOffset;
  const body = e.node.firstChild!;
  const parts = childrenOf(e.node);
  parts[0] = body.copy(body.content.cut(0, offset));
  loc.siblings[loc.index].node = e.node.copy(Fragment.fromArray(parts));
  const next = schema.nodes.outlineItem.create(
    { id: uid(), level: e.node.attrs.level },
    schema.nodes.body.create(null, body.content.cut(offset)),
  );
  loc.siblings.splice(loc.index + 1, 0, unpack(next));
  return commitTree(state, dispatch, roots.map(pack), {
    id: next.attrs.id,
    field: "body",
    offset: 0,
  });
};
export const backspaceItem: Command = (state, dispatch) => {
  if (
    !state.selection.empty ||
    state.selection.$from.parentOffset !== 0 ||
    state.selection.$from.parent.type.name !== "body"
  )
    return false;
  const e = currentEntry(state);
  if (!e) return false;
  if (e.parent) return editTree("outdent", [e.id])(state, dispatch);
  const roots = childrenOf(state.doc).slice(1).map(unpack);
  const loc = locate(roots, e.id)!;
  if (loc.index === 0) return true;
  const previous = roots[loc.index - 1],
    here = roots[loc.index];
  const body = previous.node.firstChild!;
  const before = childrenOf(previous.node).find(
    (n) => n.type.name === "description",
  );
  const after = childrenOf(here.node).find(
    (n) => n.type.name === "description",
  );
  const desc =
    before && after
      ? before.copy(
          before.content
            .append(Fragment.from(schema.nodes.hard_break.create()))
            .append(after.content),
        )
      : before || after;
  previous.node = previous.node.copy(
    Fragment.fromArray([
      body.copy(body.content.append(here.node.firstChild!.content)),
      ...(desc ? [desc] : []),
    ]),
  );
  previous.children.push(...here.children);
  roots.splice(loc.index, 1);
  return commitTree(state, dispatch, roots.map(pack), {
    id: previous.node.attrs.id,
    field: "body",
    offset: body.content.size,
  });
};
export const toggleDescription: Command = (state, dispatch) => {
  const e = currentEntry(state);
  if (!e) return false;
  const tr = state.tr;
  let pos: number;
  if (state.selection.$from.parent.type.name === "description") pos = e.pos + 2;
  else {
    const existing = textPosition(state.doc, e.id, "description");
    if (existing !== undefined) pos = existing;
    else {
      const insert = e.pos + 1 + e.node.firstChild!.nodeSize;
      tr.insert(insert, schema.nodes.description.create());
      pos = insert + 1;
    }
  }
  if (dispatch)
    dispatch(
      tr.setSelection(TextSelection.create(tr.doc, pos)).scrollIntoView(),
    );
  return true;
};
export function setLevel(ids: string[], level: number): Command {
  return (state, dispatch) => {
    const tr = state.tr;
    entries(state.doc)
      .filter((e) => ids.includes(e.id))
      .forEach((e) =>
        tr.setNodeMarkup(e.pos, undefined, { ...e.node.attrs, level }),
      );
    if (dispatch) dispatch(tr);
    return tr.docChanged;
  };
}
export function parseOutline(text: string): PMNode[] {
  const roots: Tree[] = [];
  const stack: { indent: number; tree: Tree }[] = [];
  for (const line of text.replace(/\r\n?/g, "\n").split("\n")) {
    if (!line.trim()) continue;
    const prefix = line.match(/^[\t ]*/)?.[0] || "";
    const indent = prefix.replace(/\t/g, "  ").length;
    const content = line.trim().replace(/^(?:[-*+] |\d+[.)] )/, "");
    const tree = unpack(item(content));
    while (stack.length && stack.at(-1)!.indent >= indent) stack.pop();
    (stack.at(-1)?.tree.children || roots).push(tree);
    stack.push({ indent, tree });
  }
  return roots.length ? roots.map(pack) : [item()];
}
export interface Match {
  from: number;
  to: number;
  id?: string;
}
export function findMatches(doc: PMNode, query: string): Match[] {
  if (!query) return [];
  const result: Match[] = [];
  doc.descendants((node, pos) => {
    if (!node.isTextblock) return;
    const text = node.textBetween(0, node.content.size, "", "\n");
    let index = text.indexOf(query);
    while (index >= 0) {
      result.push({
        from: pos + 1 + index,
        to: pos + 1 + index + query.length,
      });
      index = text.indexOf(query, index + query.length);
    }
    return false;
  });
  const all = entries(doc);
  return result.map((m) => ({
    ...m,
    id: [...all]
      .reverse()
      .find((e) => m.from > e.pos && m.to < e.pos + e.node.nodeSize)?.id,
  }));
}
export function replaceMatches(matches: Match[], replacement: string): Command {
  return (state, dispatch) => {
    if (!matches.length) return false;
    const tr = closeHistory(state.tr);
    [...matches]
      .sort((a, b) => b.from - a.from)
      .forEach((m) => tr.insertText(replacement, m.from, m.to));
    if (dispatch) dispatch(closeHistory(tr));
    return true;
  };
}
