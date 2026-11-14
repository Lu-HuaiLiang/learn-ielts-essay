import {
  DOMParser,
  DOMSerializer,
  Fragment,
  Node as PMNode,
  Slice,
} from "prosemirror-model";
import {
  Command,
  EditorState,
  Plugin,
  PluginKey,
  TextSelection,
} from "prosemirror-state";
import {
  Decoration,
  DecorationSet,
  EditorView,
  NodeView,
} from "prosemirror-view";
import { baseKeymap, toggleMark } from "prosemirror-commands";
import { history, redo, undo } from "prosemirror-history";
import { keymap } from "prosemirror-keymap";
import {
  backspaceItem,
  childrenOf,
  currentEntry,
  editTree,
  entries,
  findMatches,
  freshIds,
  item,
  Match,
  parseOutline,
  replaceMatches,
  safeLink,
  schema,
  selectionIds,
  splitItem,
  textPosition,
  toggleDescription,
  topEntries,
  TreeAction,
  uid,
} from "./model";

export interface UIState {
  collapsed: Set<string>;
  selected: Set<string>;
  focus: string | null;
  compact: boolean;
  query: string;
  matches: Match[];
  matchIndex: number;
}
export interface EditorEvents {
  change: () => void;
  search: () => void;
  help: () => void;
  escape: () => void;
}
const uiKey = new PluginKey<UIState>("outline-ui");
const MIME = "application/x-outline-nodes";
const colors = [
  "#333333",
  "#d95050",
  "#c49a27",
  "#509367",
  "#4487cc",
  "#9362b9",
];
const highlights = [
  "#fff0a8",
  "#ffd9d9",
  "#e7e7e7",
  "#dcf0d7",
  "#dcedff",
  "#f8dded",
  "#d5f2f1",
];

class OutlineNodeView implements NodeView {
  dom: HTMLElement;
  contentDOM: HTMLElement;
  private node: PMNode;
  constructor(node: PMNode) {
    this.node = node;
    this.dom = document.createElement("div");
    this.dom.className = "outline-item";
    const controls = document.createElement("div");
    controls.className = "node-controls";
    controls.contentEditable = "false";
    const dot = document.createElement("button");
    dot.className = "bullet";
    dot.dataset.action = "fold";
    dot.draggable = true;
    dot.innerHTML =
      '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><g class="bullet-visual"><circle class="bullet-halo" cx="12" cy="12" r="10"/><circle class="bullet-dot" cx="12" cy="12" r="3"/></g></svg>';
    controls.append(dot);
    this.contentDOM = document.createElement("div");
    this.contentDOM.className = "item-content";
    this.dom.append(controls, this.contentDOM);
    this.update(node);
  }
  update(node: PMNode) {
    if (node.type !== this.node.type) return false;
    this.node = node;
    this.dom.dataset.id = node.attrs.id;
    this.dom.dataset.level = String(node.attrs.level);
    const hasChildren = childrenOf(node).some(
      (n) => n.type.name === "outlineItem",
    );
    this.dom.classList.toggle("has-children", hasChildren);
    this.dom
      .querySelector(".bullet")!
      .setAttribute(
        "aria-label",
        `${hasChildren ? "展开或折叠" : "主题"}：${node.firstChild!.textContent || "空主题"}`,
      );
    return true;
  }
  stopEvent() {
    return false;
  }
  ignoreMutation(
    mutation: MutationRecord | { type: "selection"; target: Node },
  ) {
    return (
      mutation.type !== "selection" &&
      !this.contentDOM.contains(mutation.target)
    );
  }
}

export class OutlineEditor {
  view: EditorView;
  private events: EditorEvents;
  private dragIds: string[] = [];
  private drop: {
    id: string;
    placement: "before" | "after" | "inside";
  } | null = null;
  private anchor: string | null = null;
  constructor(element: HTMLElement, doc: PMNode, events: EditorEvents) {
    this.events = events;
    const initial: UIState = {
      collapsed: new Set(),
      selected: new Set(),
      focus: null,
      compact: false,
      query: "",
      matches: [],
      matchIndex: 0,
    };
    const uiPlugin = new Plugin<UIState>({
      key: uiKey,
      state: {
        init: () => initial,
        apply: (tr, old, _oldState, newState) => {
          const next = { ...old, ...tr.getMeta(uiKey) };
          if (tr.docChanged) {
            next.matches = findMatches(tr.doc, next.query);
            next.matchIndex = Math.min(
              next.matchIndex,
              Math.max(0, next.matches.length - 1),
            );
            const alive = new Set(entries(tr.doc).map((e) => e.id));
            next.selected = new Set(
              [...next.selected].filter((id) => alive.has(id)),
            );
            if (next.focus && !alive.has(next.focus)) next.focus = null;
            if (next.focus) {
              const all = entries(tr.doc),
                active = currentEntry(newState),
                focused = all.find((e) => e.id === next.focus);
              if (
                active &&
                active.id !== next.focus &&
                !active.ancestors.includes(next.focus)
              )
                next.focus =
                  [...(focused?.ancestors || [])]
                    .reverse()
                    .find((id) => active.ancestors.includes(id)) || null;
            }
          }
          return next;
        },
      },
      props: {
        decorations: (state) => {
          const ui = uiKey.getState(state)!;
          const all = entries(state.doc);
          const focused = all.find((e) => e.id === ui.focus);
          const active = currentEntry(state);
          const decos: Decoration[] = [];
          // DOM child selectors ignore text nodes: text + <br> + text is not empty.
          state.doc.descendants((node, pos) => {
            if (!node.isTextblock) return;
            if (node.content.size === 0) {
              decos.push(
                Decoration.node(pos, pos + node.nodeSize, {
                  class: "is-empty",
                }),
              );
            }
            return false;
          });
          for (const e of all) {
            const ancestorsOfFocus = focused?.ancestors.includes(e.id);
            const hidden =
              focused &&
              e.id !== focused.id &&
              !e.ancestors.includes(focused.id) &&
              !ancestorsOfFocus;
            const classes = [
              ui.collapsed.has(e.id) ? "is-collapsed" : "",
              ui.selected.has(e.id) ? "is-selected" : "",
              active?.id === e.id ? "is-editing" : "",
              hidden ? "is-hidden" : "",
              ancestorsOfFocus ? "focus-ancestor" : "",
              e.id === ui.focus ? "focus-root" : "",
              active?.id === e.id &&
              state.selection.$from.parent.type.name === "description"
                ? "description-active"
                : "",
            ]
              .filter(Boolean)
              .join(" ");
            decos.push(
              Decoration.node(e.pos, e.pos + e.node.nodeSize, {
                class: classes,
                "data-depth": String(e.depth),
              }),
            );
          }
          ui.matches.forEach((m, i) =>
            decos.push(
              Decoration.inline(m.from, m.to, {
                class: `search-match ${i === ui.matchIndex ? "current-match" : ""}`,
              }),
            ),
          );
          return DecorationSet.create(state.doc, decos);
        },
        handleKeyDown: (_view, event) => {
          if (event.key === "Escape") {
            this.setUI({ selected: new Set() });
            this.events.escape();
            return true;
          }
          return false;
        },
      },
    });
    const commands: Record<string, Command> = {
      Enter: splitItem,
      Tab: () => {
        this.tree("indent");
        return true;
      },
      "Shift-Tab": () => {
        this.tree("outdent");
        return true;
      },
      Backspace: (state, dispatch) =>
        this.ui.selected.size
          ? editTree("delete", this.ids)(state, dispatch)
          : backspaceItem(state, dispatch),
      Delete: (state, dispatch) =>
        this.ui.selected.size
          ? editTree("delete", this.ids)(state, dispatch)
          : this.forwardDelete(state, dispatch),
      "Shift-Enter": toggleDescription,
      "Mod-z": undo,
      "Mod-Shift-z": redo,
      "Mod-y": redo,
      "Mod-d": () => {
        this.tree("duplicate");
        return true;
      },
      "Mod-Shift-Backspace": () => {
        this.tree("delete");
        return true;
      },
      "Mod-Shift-ArrowUp": () => {
        this.tree("up");
        return true;
      },
      "Mod-Shift-ArrowDown": () => {
        this.tree("down");
        return true;
      },
      "Mod-b": () => this.format("bold"),
      "Mod-i": () => this.format("italic"),
      "Mod-u": () => this.format("underline"),
      "Mod-Enter": () => this.format("strike"),
      "Mod-f": () => {
        this.events.search();
        return true;
      },
      "Mod-/": () => {
        this.events.help();
        return true;
      },
      "Mod-.": () => {
        this.fold();
        return true;
      },
      "Alt-.": () => {
        this.fold();
        return true;
      },
      "Mod-Shift-.": () => {
        this.foldSiblings();
        return true;
      },
      "Mod-Alt-Shift-.": () => {
        this.foldAll();
        return true;
      },
      "Mod-]": () => {
        this.focus(this.ids[0] || null);
        return true;
      },
      "Mod-[": () => {
        this.focusParent();
        return true;
      },
      "Shift-ArrowUp": () => this.extendNodes(-1),
      "Shift-ArrowDown": () => this.extendNodes(1),
      "Mod-a": (state) => {
        const e = currentEntry(state);
        if (this.ui.selected.size || !state.selection.empty) {
          this.setUI({
            selected: new Set(this.visibleEntries().map((e) => e.id)),
          });
          return true;
        }
        if (e) {
          const from = state.selection.$from.start();
          this.view.dispatch(
            state.tr.setSelection(
              TextSelection.create(
                state.doc,
                from,
                from + state.selection.$from.parent.content.size,
              ),
            ),
          );
          return true;
        }
        return false;
      },
      ArrowDown: () => this.navigate(1),
      ArrowUp: () => this.navigate(-1),
    };
    for (let n = 1; n <= 3; n++) {
      commands[`Mod-Alt-${n}`] = () => {
        this.foldTo(n);
        return true;
      };
    }
    ["d", "r", "y", "g", "b", "p"].forEach(
      (k, i) =>
        (commands[`Alt-${k}`] = () =>
          this.format("color", { color: colors[i] })),
    );
    ["y", "r", "h", "g", "b", "p", "c"].forEach(
      (k, i) =>
        (commands[`Mod-Alt-${k}`] = () =>
          this.format("highlight", { color: highlights[i] })),
    );
    this.view = new EditorView(element, {
      state: EditorState.create({
        doc,
        plugins: [
          uiPlugin,
          keymap(commands),
          keymap(baseKeymap),
          history({ depth: 200 }),
        ],
      }),
      attributes: {
        class: "outline-document",
        spellcheck: "false",
        "aria-label": "大纲编辑器",
        role: "textbox",
        "aria-multiline": "true",
      },
      nodeViews: { outlineItem: (node) => new OutlineNodeView(node) },
      dispatchTransaction: (tr) => {
        this.view.updateState(this.view.state.apply(tr));
        this.events.change();
      },
      handleDOMEvents: {
        keydown: (view, event) => {
          // Some IMEs send keydown before compositionstart or after compositionend.
          // Returning true here skips editor shortcuts WITHOUT preventDefault,
          // leaving candidate selection and native composition markers to the IME.
          if (view.composing || event.isComposing || event.keyCode === 229)
            return true;
          this.syncDOMSelection();
          return false;
        },
        mousedown: (_view, event) => {
          const el = event.target as HTMLElement;
          const row = el.closest<HTMLElement>(".outline-item");
          if (el.closest(".node-controls")) {
            if (!el.closest(".bullet")) event.preventDefault();
            return true;
          }
          if (row && event.shiftKey && this.ui.selected.size) {
            event.preventDefault();
            this.selectNode(row.dataset.id!, true);
            return true;
          }
          if (this.ui.selected.size) this.setUI({ selected: new Set() });
          return false;
        },
        click: (_view, event) => {
          const el = event.target as HTMLElement;
          const action =
            el.closest<HTMLElement>("[data-action]")?.dataset.action;
          const row = el.closest<HTMLElement>(".outline-item");
          if (row && action) {
            event.preventDefault();
            const id = row.dataset.id!;
            if (event.shiftKey) {
              this.selectNode(id, true);
              return true;
            }
            if (action === "fold" && row.classList.contains("has-children"))
              this.fold(id);
            return true;
          }
          const a = el.closest<HTMLAnchorElement>("a");
          if (a) {
            event.preventDefault();
            if (event.metaKey || event.ctrlKey) {
              const href = safeLink(a.getAttribute("href") || "");
              if (href) window.open(href, "_blank", "noopener,noreferrer");
            }
            return true;
          }
          return false;
        },
        copy: (_v, e) => this.copy(e),
        cut: (_v, e) => this.copy(e, true),
        dragstart: (_view, event) => {
          const row = (event.target as HTMLElement).closest<HTMLElement>(
            ".outline-item",
          );
          if (!row || !(event.target as HTMLElement).closest(".bullet"))
            return false;
          this.dragIds = this.ui.selected.has(row.dataset.id!)
            ? this.ids
            : [row.dataset.id!];
          event.dataTransfer!.setData("text/plain", "移动主题");
          event.dataTransfer!.effectAllowed = "move";
          row.classList.add("is-dragging");
          return true;
        },
        dragover: (_v, event) => {
          if (!this.dragIds.length) return false;
          event.preventDefault();
          this.clearDrop();
          const row = (event.target as HTMLElement).closest<HTMLElement>(
            ".outline-item",
          );
          if (!row) return true;
          const rect = row.querySelector(".node-body")!.getBoundingClientRect();
          const placement =
            event.clientX > rect.left + 40
              ? "inside"
              : event.clientY < rect.top + rect.height / 2
                ? "before"
                : "after";
          if (
            editTree("move", this.dragIds, {
              target: row.dataset.id!,
              placement,
            })(this.view.state)
          ) {
            this.drop = { id: row.dataset.id!, placement };
            row.classList.add(`drop-${placement}`);
            event.dataTransfer!.dropEffect = "move";
          }
          return true;
        },
        drop: (_v, event) => {
          if (!this.dragIds.length) return false;
          event.preventDefault();
          if (this.drop) {
            const { id, placement } = this.drop;
            this.run(editTree("move", this.dragIds, { target: id, placement }));
            if (placement === "inside") {
              const collapsed = new Set(this.ui.collapsed);
              collapsed.delete(id);
              this.setUI({ collapsed });
            }
          }
          this.endDrag();
          return true;
        },
        dragend: () => {
          this.endDrag();
          return false;
        },
      },
      handlePaste: (_view, event, slice) => this.paste(event, slice),
      handleTextInput: (_view, _from, _to, text) => {
        if (!this.ui.selected.size) return false;
        this.run(editTree("replace", this.ids, { nodes: [item(text)] }));
        this.setUI({ selected: new Set() });
        return true;
      },
      transformPasted: (slice) =>
        new Slice(
          Fragment.fromArray(childrenOfSlice(slice.content).map(freshIds)),
          slice.openStart,
          slice.openEnd,
        ),
    });
  }
  private syncDOMSelection() {
    if (this.ui.selected.size || this.view.composing) return;
    const selection = window.getSelection();
    if (
      !selection?.anchorNode ||
      !selection.focusNode ||
      !this.view.dom.contains(selection.anchorNode) ||
      !this.view.dom.contains(selection.focusNode)
    )
      return;
    try {
      const anchor = this.view.posAtDOM(
          selection.anchorNode,
          selection.anchorOffset,
        ),
        head = this.view.posAtDOM(selection.focusNode, selection.focusOffset);
      if (
        anchor === this.state.selection.anchor &&
        head === this.state.selection.head
      )
        return;
      if (
        this.state.doc.resolve(anchor).parent.inlineContent &&
        this.state.doc.resolve(head).parent.inlineContent
      )
        this.view.dispatch(
          this.state.tr.setSelection(
            TextSelection.create(this.state.doc, anchor, head),
          ),
        );
    } catch {
      /* A native composition can temporarily detach a DOM selection. */
    }
  }
  get state() {
    return this.view.state;
  }
  get ui() {
    return uiKey.getState(this.state)!;
  }
  get ids() {
    return this.ui.selected.size
      ? [...this.ui.selected]
      : selectionIds(this.state);
  }
  setUI(patch: Partial<UIState>) {
    if (patch.selected?.size === 0) this.anchor = null;
    const tr = this.state.tr;
    if (patch.collapsed) {
      const all = entries(this.state.doc),
        focus = all.find(
          (e) =>
            e.id === (patch.focus === undefined ? this.ui.focus : patch.focus),
        );
      focus?.ancestors.forEach((id) => patch.collapsed!.delete(id));
      const hidden = currentEntry(this.state)?.ancestors.find((id) =>
        patch.collapsed!.has(id),
      );
      if (hidden) {
        tr.setSelection(
          TextSelection.create(
            this.state.doc,
            textPosition(this.state.doc, hidden)!,
          ),
        );
        patch.selected = new Set();
        this.anchor = null;
      }
    }
    this.view.dispatch(tr.setMeta(uiKey, patch).setMeta("addToHistory", false));
  }
  run(command: Command) {
    const success = command(
      this.state,
      (tr) => this.view.dispatch(tr),
      this.view,
    );
    if (success) this.view.focus();
    return success;
  }
  tree(action: TreeAction) {
    const ids = this.ids;
    const success = this.run(editTree(action, ids));
    if (success) {
      if (action === "indent") {
        const collapsed = new Set(this.ui.collapsed);
        entries(this.state.doc)
          .filter((e) => ids.includes(e.id))
          .forEach((e) => e.ancestors.forEach((id) => collapsed.delete(id)));
        this.setUI({ collapsed });
      }
      if (action === "delete") this.setUI({ selected: new Set() });
    }
    return success;
  }
  selectNode(id: string, extend: boolean) {
    const visible = this.visibleEntries();
    let selected = new Set([id]);
    if (extend) {
      const anchor = this.anchor || currentEntry(this.state)?.id || id;
      const a = visible.findIndex((e) => e.id === anchor),
        b = visible.findIndex((e) => e.id === id);
      if (a >= 0 && b >= 0)
        selected = new Set(
          visible.slice(Math.min(a, b), Math.max(a, b) + 1).map((e) => e.id),
        );
    } else this.anchor = id;
    const pos = textPosition(this.state.doc, id);
    if (pos !== undefined)
      this.view.dispatch(
        this.state.tr
          .setSelection(TextSelection.create(this.state.doc, pos))
          .setMeta(uiKey, { selected }),
      );
    this.view.focus();
  }
  extendNodes(direction: number) {
    const id = currentEntry(this.state)?.id;
    if (!id) return false;
    const visible = this.visibleEntries();
    const head = id;
    const index = visible.findIndex((e) => e.id === head);
    const next = visible[index + direction];
    if (!next) return true;
    if (!this.ui.selected.size) this.anchor = id;
    this.selectNode(next.id, true);
    return true;
  }
  visibleEntries() {
    const all = entries(this.state.doc);
    const focused = all.find((e) => e.id === this.ui.focus);
    return all.filter(
      (e) =>
        (!focused || e.id === focused.id || e.ancestors.includes(focused.id)) &&
        !e.ancestors.some((id) => this.ui.collapsed.has(id)),
    );
  }
  navigate(direction: number) {
    if (!this.state.selection.empty) return false;
    const e = currentEntry(this.state);
    if (!e) return false;
    const $p = this.state.selection.$from;
    const boundary =
      direction < 0
        ? $p.parentOffset === 0
        : $p.parentOffset === $p.parent.content.size;
    if (!boundary) return false;
    const visible = this.visibleEntries();
    const next = visible[visible.findIndex((n) => n.id === e.id) + direction];
    if (!next) return false;
    const pos = textPosition(
      this.state.doc,
      next.id,
      "body",
      direction < 0 ? next.node.firstChild!.content.size : 0,
    )!;
    this.view.dispatch(
      this.state.tr
        .setSelection(TextSelection.create(this.state.doc, pos))
        .setMeta(uiKey, { selected: new Set() })
        .scrollIntoView(),
    );
    return true;
  }
  forwardDelete(state: EditorState, dispatch: Parameters<Command>[1]) {
    if (
      !state.selection.empty ||
      state.selection.$from.parent.type.name !== "body" ||
      state.selection.$from.parentOffset !==
        state.selection.$from.parent.content.size
    )
      return false;
    // A boundary Delete must not let the generic block join absorb a description or child.
    const e = currentEntry(state);
    if (!e) return false;
    const all = entries(state.doc);
    const siblings = all.filter((n) => n.parent === e.parent);
    const next = siblings[siblings.findIndex((n) => n.id === e.id) + 1];
    if (!next || e.parent) return true;
    const staged = state.apply(
      state.tr.setSelection(TextSelection.create(state.doc, next.pos + 2)),
    );
    return backspaceItem(staged, (tr) =>
      dispatch?.(
        state.tr
          .replaceWith(0, state.doc.content.size, tr.doc.content)
          .setSelection(tr.selection),
      ),
    );
  }
  format(mark: string, attrs?: Record<string, string>) {
    const type = schema.marks[mark];
    if (!type) return false;
    if (this.ui.selected.size) {
      const tr = this.state.tr;
      const selected = entries(this.state.doc).filter((e) =>
        this.ui.selected.has(e.id),
      );
      const allHave = selected.every((e) =>
        this.state.doc.rangeHasMark(
          e.pos + 2,
          e.pos + 2 + e.node.firstChild!.content.size,
          type,
        ),
      );
      selected.forEach((e) => {
        const from = e.pos + 2,
          to = from + e.node.firstChild!.content.size;
        if (allHave && !attrs) tr.removeMark(from, to, type);
        else tr.addMark(from, to, type.create(attrs));
      });
      this.view.dispatch(tr);
      this.view.focus();
      return true;
    }
    return this.run(toggleMark(type, attrs));
  }
  fold(id = this.ids[0]) {
    if (!id) return;
    const collapsed = new Set(this.ui.collapsed);
    collapsed.has(id) ? collapsed.delete(id) : collapsed.add(id);
    this.setUI({ collapsed });
    const active = currentEntry(this.state);
    if (active?.ancestors.includes(id)) {
      const pos = textPosition(this.state.doc, id)!;
      this.view.dispatch(
        this.state.tr.setSelection(TextSelection.create(this.state.doc, pos)),
      );
    }
  }
  foldSiblings() {
    const e = entries(this.state.doc).find((e) => e.id === this.ids[0]);
    if (!e) return;
    const collapsed = new Set(this.ui.collapsed);
    const close = !collapsed.has(e.id);
    entries(this.state.doc)
      .filter((n) => n.parent === e.parent)
      .forEach((n) => (close ? collapsed.add(n.id) : collapsed.delete(n.id)));
    this.setUI({ collapsed });
  }
  foldAll(close?: boolean) {
    const shouldClose = close ?? this.ui.collapsed.size === 0;
    this.setUI({
      collapsed: shouldClose
        ? new Set(entries(this.state.doc).map((e) => e.id))
        : new Set(),
    });
  }
  foldTo(depth: number) {
    this.setUI({
      collapsed: new Set(
        entries(this.state.doc)
          .filter((e) => e.depth >= depth - 1)
          .map((e) => e.id),
      ),
    });
  }
  focus(id: string | null) {
    const collapsed = new Set(this.ui.collapsed);
    const e = entries(this.state.doc).find((e) => e.id === id);
    if (e) [...e.ancestors, e.id].forEach((id) => collapsed.delete(id));
    this.setUI({ focus: id, selected: new Set(), collapsed });
    if (e)
      this.view.dispatch(
        this.state.tr.setSelection(
          TextSelection.create(this.state.doc, e.pos + 2),
        ),
      );
  }
  focusParent() {
    const e = entries(this.state.doc).find((e) => e.id === this.ui.focus);
    this.focus(e?.parent || null);
  }
  search(query: string) {
    const matches = findMatches(this.state.doc, query);
    this.setUI({ query, matches, matchIndex: 0 });
    if (matches.length) this.reveal(0, false);
  }
  reveal(index: number, focus = false) {
    const matches = this.ui.matches;
    if (!matches.length) return;
    index = (index + matches.length) % matches.length;
    const m = matches[index];
    const collapsed = new Set(this.ui.collapsed);
    const e = entries(this.state.doc).find((e) => e.id === m.id);
    e?.ancestors.forEach((id) => collapsed.delete(id));
    this.setUI({ collapsed, matchIndex: index, focus: null });
    this.view.dispatch(
      this.state.tr
        .setSelection(TextSelection.create(this.state.doc, m.from, m.to))
        .scrollIntoView(),
    );
    if (focus) this.view.focus();
  }
  replace(text: string, all: boolean) {
    const matches = all
      ? this.ui.matches
      : this.ui.matches.slice(this.ui.matchIndex, this.ui.matchIndex + 1);
    replaceMatches(matches, text)(this.state, (tr) => this.view.dispatch(tr));
    if (this.ui.matches.length)
      this.reveal(Math.min(this.ui.matchIndex, this.ui.matches.length - 1));
  }
  private copy(event: ClipboardEvent, cut = false) {
    if (!this.ui.selected.size) return false;
    const nodes = topEntries(this.state.doc, this.ids).map((e) => e.node);
    const data = event.clipboardData;
    if (!data) return false;
    event.preventDefault();
    data.setData(MIME, JSON.stringify(nodes.map((n) => n.toJSON())));
    const wrapper = document.createElement("div");
    wrapper.append(
      DOMSerializer.fromSchema(schema).serializeFragment(
        Fragment.fromArray(nodes),
      ),
    );
    data.setData("text/html", wrapper.innerHTML);
    data.setData("text/plain", nodes.map((n) => this.plain(n)).join("\n"));
    if (cut) this.tree("delete");
    return true;
  }
  private plain(node: PMNode, depth = 0): string {
    const body = node.firstChild!.textContent;
    const desc = childrenOf(node).find((n) => n.type.name === "description");
    return `${"  ".repeat(depth)}${body}${
      desc
        ? "\n" +
          desc
            .textBetween(0, desc.content.size, "", "\n")
            .split("\n")
            .map((s) => "  ".repeat(depth + 1) + s)
            .join("\n")
        : ""
    }${childrenOf(node)
      .filter((n) => n.type.name === "outlineItem")
      .map((n) => "\n" + this.plain(n, depth + 1))
      .join("")}`;
  }
  private paste(event: ClipboardEvent, slice: Slice) {
    const data = event.clipboardData;
    if (!data) return false;
    const text = data.getData("text/plain"),
      raw = data.getData(MIME),
      html = data.getData("text/html");
    const field = this.state.selection.$from.parent.type.name;
    if (field === "description") {
      if (text) {
        event.preventDefault();
        const fragment = Fragment.fromArray(
          text
            .replace(/\r\n?/g, "\n")
            .split("\n")
            .flatMap((line, i) => [
              ...(i ? [schema.nodes.hard_break.create()] : []),
              ...(line ? [schema.text(line)] : []),
            ]),
        );
        this.view.dispatch(
          this.state.tr
            .replaceSelection(new Slice(fragment, 0, 0))
            .scrollIntoView(),
        );
        return true;
      }
      return false;
    }
    if (field === "title") {
      event.preventDefault();
      this.view.dispatch(
        this.state.tr
          .insertText(text.replace(/\s*\n\s*/g, " "))
          .scrollIntoView(),
      );
      return true;
    }
    let nodes: PMNode[] = [];
    if (raw) {
      try {
        const json = JSON.parse(raw);
        if (Array.isArray(json))
          nodes = json
            .map((n) => {
              const node = schema.nodeFromJSON(n);
              node.check();
              return freshIds(node);
            })
            .filter((n) => n.type.name === "outlineItem");
      } catch {
        nodes = [];
      }
    }
    if (!nodes.length && html.includes("data-outline")) {
      const el = document.createElement("div");
      el.innerHTML = html;
      const parsed = DOMParser.fromSchema(schema).parseSlice(el);
      nodes = childrenOfSlice(parsed.content)
        .filter((n) => n.type.name === "outlineItem")
        .map(freshIds);
    }
    if (!nodes.length && /\n/.test(text) && !html) nodes = parseOutline(text);
    if (!nodes.length && html) {
      const blocks = childrenOfSlice(slice.content);
      if (blocks.length > 1)
        nodes = blocks
          .filter((n) => n.isTextblock)
          .map((n) =>
            schema.nodes.outlineItem.create(
              { id: uid() },
              schema.nodes.body.create(null, n.content),
            ),
          );
    }
    if (!nodes.length && this.ui.selected.size) {
      const blocks = childrenOfSlice(slice.content);
      const content = blocks[0]?.isTextblock
        ? blocks[0].content
        : slice.content;
      nodes =
        html &&
        content.size &&
        childrenOfSlice(content).every((n) => n.isInline)
          ? [
              schema.nodes.outlineItem.create(
                { id: uid() },
                schema.nodes.body.create(null, content),
              ),
            ]
          : [item(text)];
    }
    if (nodes.length) {
      event.preventDefault();
      const e = currentEntry(this.state);
      if (!e) return false;
      const tr = this.state.tr;
      const empty =
        e.node.firstChild!.content.size === 0 && e.node.childCount === 1;
      const from = empty ? e.pos : e.pos + e.node.nodeSize,
        to = empty ? e.pos + e.node.nodeSize : from;
      if (this.ui.selected.size) {
        const selected = topEntries(this.state.doc, this.ids);
        for (const selectedEntry of selected.slice(1).reverse())
          tr.delete(
            selectedEntry.pos,
            selectedEntry.pos + selectedEntry.node.nodeSize,
          );
        const first = selected[0];
        tr.replaceWith(first.pos, first.pos + first.node.nodeSize, nodes);
      } else tr.replaceWith(from, to, nodes);
      const pos = textPosition(
        tr.doc,
        nodes.at(-1)!.attrs.id,
        "body",
        nodes.at(-1)!.firstChild!.content.size,
      )!;
      this.view.dispatch(
        tr
          .setSelection(TextSelection.create(tr.doc, pos))
          .setMeta(uiKey, { selected: new Set() })
          .scrollIntoView(),
      );
      return true;
    }
    return false;
  }
  private clearDrop() {
    this.view.dom
      .querySelectorAll(".drop-before,.drop-after,.drop-inside")
      .forEach((el) =>
        el.classList.remove("drop-before", "drop-after", "drop-inside"),
      );
    this.drop = null;
  }
  private endDrag() {
    this.clearDrop();
    this.dragIds = [];
    this.view.dom
      .querySelectorAll(".is-dragging")
      .forEach((el) => el.classList.remove("is-dragging"));
  }
  destroy() {
    this.view.destroy();
  }
}
function childrenOfSlice(fragment: Fragment) {
  const nodes: PMNode[] = [];
  fragment.forEach((n) => nodes.push(n));
  return nodes;
}
export { colors, highlights, undo, redo, toggleDescription };
