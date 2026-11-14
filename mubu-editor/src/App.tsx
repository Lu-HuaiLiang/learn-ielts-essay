import { useEffect, useLayoutEffect, useRef, useState } from "react";
import {
  Bold,
  ChevronLeft,
  ChevronRight,
  ChevronsDownUp,
  ChevronsUpDown,
  Ellipsis,
  Highlighter,
  Italic,
  ListTree,
  Redo2,
  Search,
  Settings2,
  Strikethrough,
  Underline,
  Undo2,
  X,
  Keyboard,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  OutlineEditor,
  colors,
  highlights,
  undo,
  redo,
} from "./editor/controller";
import { entries } from "./editor/model";
import type { Node as PMNode } from "prosemirror-model";

const fontSizePreferenceKey = "ielts-essay.mubu.font-size.v1";
function loadFontSize() {
  try {
    const saved = Number(localStorage.getItem(fontSizePreferenceKey));
    if (Number.isInteger(saved) && saved >= 14 && saved <= 24) return saved;
  } catch {
    // Storage restrictions must not prevent editing.
  }
  return 15;
}


const isMac =
  typeof navigator !== "undefined" && /Mac/.test(navigator.platform);
const mod = isMac ? "⌘" : "Ctrl";
function IconButton({
  label,
  icon: Icon,
  onClick,
  active = false,
  disabled = false,
  children,
}: {
  label: string;
  icon?: LucideIcon;
  onClick: () => void;
  active?: boolean;
  disabled?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <button
      type="button"
      className={`icon-button ${active ? "active" : ""}`}
      title={label}
      aria-label={label}
      disabled={disabled}
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
    >
      {Icon ? <Icon size={17} strokeWidth={1.7} /> : children}
    </button>
  );
}
function MenuItem({
  icon: Icon,
  label,
  shortcut,
  onClick,
  danger = false,
}: {
  icon: LucideIcon;
  label: string;
  shortcut?: string;
  onClick: () => void;
  danger?: boolean;
}) {
  return (
    <button
      type="button"
      className={`menu-item ${danger ? "danger" : ""}`}
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
    >
      <Icon size={16} />
      <span>{label}</span>
      {shortcut && <kbd>{shortcut}</kbd>}
    </button>
  );
}
function FormatBar({ editor }: { editor: OutlineEditor }) {
  const [palette, setPalette] = useState<"color" | "highlight" | null>(null);
  const marks =
    editor.state.storedMarks || editor.state.selection.$from.marks();
  const marked = (name: string) =>
    editor.ui.selected.size === 0 && marks.some((m) => m.type.name === name);
  return (
    <div className="format-bar" role="toolbar" aria-label="文字格式">
      <div className="format-row">
        <IconButton
          label="加粗"
          icon={Bold}
          active={marked("bold")}
          onClick={() => editor.format("bold")}
        />
        <IconButton
          label="斜体"
          icon={Italic}
          active={marked("italic")}
          onClick={() => editor.format("italic")}
        />
        <IconButton
          label="下划线"
          icon={Underline}
          active={marked("underline")}
          onClick={() => editor.format("underline")}
        />
        <IconButton
          label="删除线"
          icon={Strikethrough}
          active={marked("strike")}
          onClick={() => editor.format("strike")}
        />
        <span className="toolbar-divider" />
        <IconButton
          label="文字颜色"
          onClick={() => {
            setPalette(palette === "color" ? null : "color");
          }}
          active={palette === "color"}
        >
          <span className="color-icon">A</span>
        </IconButton>
        <IconButton
          label="高亮"
          icon={Highlighter}
          onClick={() => {
            setPalette(palette === "highlight" ? null : "highlight");
          }}
          active={palette === "highlight"}
        />
      </div>
      {palette && (
        <div className="palette">
          {(palette === "color" ? colors : highlights).map((color, i) => (
            <button
              key={color}
              aria-label={`${palette === "color" ? "文字颜色" : "高亮"} ${i + 1}`}
              title={color}
              style={{ background: color }}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => {
                editor.format(palette, { color });
                setPalette(null);
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
const shortcuts = [
  ["新增同级主题", "Enter"],
  ["缩进 / 提升一级", "Tab / Shift Tab"],
  ["进入 / 退出描述", "Shift Enter"],
  ["移动主题", `${mod} Shift ↑ / ↓`],
  ["多选主题", "Shift ↑ / ↓ 或 Shift 点击圆点"],
  ["复制主题副本", `${mod} D`],
  ["删除主题", `${mod} Shift Backspace`],
  ["展开 / 折叠主题", `${mod} .`],
  ["展开 / 折叠同级", `${mod} Shift .`],
  ["展开 / 折叠全部", `${mod} Alt Shift .`],
  ["展开至 1 / 2 / 3 级", `${mod} Alt 1 / 2 / 3`],
  ["进入主题 / 返回上级", `${mod} ] / [`],
  ["撤销 / 重做", `${mod} Z / ${mod} Shift Z`],
  ["加粗 / 斜体 / 下划线", `${mod} B / I / U`],
  ["删除线", `${mod} Enter`],
  ["文字颜色", "Alt D / R / Y / G / B / P"],
  ["高亮", `${mod} Alt Y / R / H / G / B / P / C`],
  ["搜索文档", `${mod} F`],
  ["页面放大 / 缩小 / 重置", `${mod} + / − / 0`],
  ["快捷键帮助", `${mod} /`],
  ["关闭面板 / 取消选择", "Esc"],
];
export default function App({initialDocument, onDocumentChange}: {initialDocument: PMNode; onDocumentChange: (doc: PMNode) => void}) {
  const mount = useRef<HTMLDivElement>(null);
  const editorRef = useRef<OutlineEditor | null>(null);
  const [revision, refresh] = useState(0);
  const [searchOpen, setSearchOpen] = useState(false);
  const [settings, setSettings] = useState(false);
  const [help, setHelp] = useState(false);
  const [query, setQuery] = useState("");
  const [replacement, setReplacement] = useState("");
  const [fontSize, setFontSize] = useState(loadFontSize);
  function changeFontSize(delta: number) {
    const next = Math.max(14, Math.min(24, fontSize + delta));
    setFontSize(next);
    try {
      localStorage.setItem(fontSizePreferenceKey, String(next));
    } catch {
      // Keep the adjustment usable even when it cannot be remembered.
    }
  }
  const [bubble, setBubble] = useState<{ x: number; y: number } | null>(null);
  useLayoutEffect(() => {
    const editor = new OutlineEditor(mount.current!, initialDocument, {
      change: () => {
        refresh((n) => n + 1);
        if (editorRef.current) onDocumentChange(editorRef.current.state.doc);
      },
      search: () => {
        setSearchOpen(true);
        setSettings(false);
      },
      help: () => setHelp(true),
      escape: () => {
        setSettings(false);
        setHelp(false);
        setSearchOpen(false);
      },
    });
    editorRef.current = editor;
    refresh((n) => n + 1);
    return () => {
      editor.destroy();
      editorRef.current = null;
    };
  }, []);
  const editor = editorRef.current;
  useEffect(() => {
    const handle = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSettings(false);
        setHelp(false);
        if (searchOpen) {
          setSearchOpen(false);
          editorRef.current?.search("");
          editorRef.current?.view.focus();
        }
      }
      if ((event.metaKey || event.ctrlKey) && event.key === "f") {
        event.preventDefault();
        setSearchOpen(true);
        setSettings(false);
      }
      if ((event.metaKey || event.ctrlKey) && event.key === "/") {
        event.preventDefault();
        setHelp((h) => !h);
      }
    };
    window.addEventListener("keydown", handle);
    return () => window.removeEventListener("keydown", handle);
  }, [searchOpen]);
  useEffect(() => {
    const update = () => {
      if (
        !editor ||
        editor.state.selection.empty ||
        editor.state.selection.from < editor.state.doc.firstChild!.nodeSize ||
        editor.ui.selected.size ||
        searchOpen
      ) {
        setBubble(null);
        return;
      }
      const selection = window.getSelection();
      if (
        !selection?.rangeCount ||
        !editor.view.dom.contains(selection.anchorNode)
      ) {
        setBubble(null);
        return;
      }
      const rect = selection.getRangeAt(0).getBoundingClientRect();
      setBubble({
        x: Math.max(
          12,
          Math.min(window.innerWidth - 240, rect.left + rect.width / 2 - 114),
        ),
        y: Math.max(
          64,
          Math.min(
            window.innerHeight - 58,
            rect.top > 90 ? rect.top - 52 : rect.bottom + 10,
          ),
        ),
      });
    };
    update();
    window.addEventListener("scroll", update);
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [revision, editor, searchOpen]);
  useEffect(() => {
    if (!settings) return;
    const close = (event: MouseEvent) => {
      if (
        !(event.target as HTMLElement).closest(
          ".popover,.format-bar,.node-controls,.settings-trigger",
        )
      ) {
        setSettings(false);
      }
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [settings]);
  const closeSearch = () => {
    setSearchOpen(false);
    setQuery("");
    editor?.search("");
    editor?.view.focus();
  };
  const all = editor ? entries(editor.state.doc) : [];
  const focusEntry = all.find((e) => e.id === editor?.ui.focus);
  const breadcrumbs = focusEntry
    ? [...focusEntry.ancestors, focusEntry.id].map((id) =>
        all.find((e) => e.id === id)!,
      )
    : [];
  return (
    <div
      className="app"
      style={{ "--editor-font-size": `${fontSize}px` } as React.CSSProperties}
    >
      <header className="app-header">
        <div className="brand">
          <span className="brand-symbol">
            <ListTree size={17} strokeWidth={1.8} />
          </span>
          <span>大纲</span>
          <span className="brand-divider" />
          <span className="session-label">本地笔记</span>
        </div>
        <div className="header-actions">
          <IconButton
            label="撤销"
            icon={Undo2}
            disabled={!editor || !undo(editor.state)}
            onClick={() => editor?.run(undo)}
          />
          <IconButton
            label="重做"
            icon={Redo2}
            disabled={!editor || !redo(editor.state)}
            onClick={() => editor?.run(redo)}
          />
          <span className="toolbar-divider" />
          <IconButton
            label="搜索与替换"
            icon={Search}
            active={searchOpen}
            onClick={() => {
              setSearchOpen(!searchOpen);
              setSettings(false);
            }}
          />
          <span className="settings-trigger">
            <IconButton
              label="更多设置"
              icon={Ellipsis}
              active={settings}
              onClick={() => {
                setSettings(!settings);
              }}
            />
          </span>
        </div>
      </header>
      {settings && editor && (
        <div className="popover settings-panel">
          <div className="panel-title">
            <Settings2 size={15} /> 编辑器设置
          </div>
          <div className="setting-row">
            <span>正文字号</span>
            <div className="size-stepper">
              <button
                aria-label="缩小字号"
                onClick={() => changeFontSize(-1)}
              >
                −
              </button>
              <span>{fontSize}</span>
              <button
                aria-label="放大字号"
                onClick={() => changeFontSize(1)}
              >
                +
              </button>
            </div>
          </div>
          <label className="setting-row">
            <span>描述仅显示首行</span>
            <input
              type="checkbox"
              checked={editor.ui.compact}
              onChange={(e) => editor.setUI({ compact: e.target.checked })}
            />
          </label>
          <div className="menu-separator" />
          <MenuItem
            icon={ChevronsUpDown}
            label="展开全部"
            onClick={() => {
              editor.foldAll(false);
              setSettings(false);
            }}
          />
          <MenuItem
            icon={ChevronsDownUp}
            label="折叠全部"
            onClick={() => {
              editor.foldAll(true);
              setSettings(false);
            }}
          />
          <div className="depth-options">
            <span>展开至</span>
            {[1, 2, 3].map((n) => (
              <button
                key={n}
                onClick={() => {
                  editor.foldTo(n);
                  setSettings(false);
                }}
              >
                {n} 级
              </button>
            ))}
          </div>
          <div className="menu-separator" />
          <MenuItem
            icon={Keyboard}
            label="快捷键"
            shortcut={`${mod} /`}
            onClick={() => {
              setHelp(true);
              setSettings(false);
            }}
          />
          <p className="settings-note">笔记自动保存到当前浏览器，刷新后可继续编辑。</p>
        </div>
      )}
      {searchOpen && editor && (
        <div className="popover search-panel" role="search">
          <div className="search-row">
            <Search size={16} />
            <input
              autoFocus
              placeholder="搜索文档"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                editor.search(e.target.value);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter")
                  editor.reveal(editor.ui.matchIndex + (e.shiftKey ? -1 : 1));
              }}
            />
            <span className="match-count">
              {editor.ui.matches.length
                ? `${editor.ui.matchIndex + 1}/${editor.ui.matches.length}`
                : "0/0"}
            </span>
            <IconButton
              label="上一个结果"
              icon={ChevronLeft}
              onClick={() => editor.reveal(editor.ui.matchIndex - 1)}
            />
            <IconButton
              label="下一个结果"
              icon={ChevronRight}
              onClick={() => editor.reveal(editor.ui.matchIndex + 1)}
            />
            <IconButton label="关闭搜索" icon={X} onClick={closeSearch} />
          </div>
          <div className="replace-row">
            <input
              placeholder="替换为"
              value={replacement}
              onChange={(e) => setReplacement(e.target.value)}
            />
            <button
              disabled={!editor.ui.matches.length}
              onClick={() => editor.replace(replacement, false)}
            >
              替换
            </button>
            <button
              disabled={!editor.ui.matches.length}
              onClick={() => editor.replace(replacement, true)}
            >
              全部替换
            </button>
          </div>
        </div>
      )}
      <main
        className={`document-shell ${editor?.ui.compact ? "compact-description" : ""} ${focusEntry ? "is-focused" : ""}`}
      >
        {focusEntry && (
          <nav className="breadcrumbs" aria-label="主题路径">
            <button
              aria-label="返回完整文档"
              onClick={() => editor?.focus(null)}
            >
              {editor?.state.doc.firstChild?.textContent || "无标题文档"}
            </button>
            {breadcrumbs.map((e) => (
              <span key={e.id}>
                <ChevronRight size={12} />
                <button onClick={() => editor?.focus(e.id)}>
                  {e.node.firstChild!.textContent || "空主题"}
                </button>
              </span>
            ))}
          </nav>
        )}
        <div ref={mount} />
        <div className="document-end">
          <span />{" "}
          <span className="end-text">
            {editor?.ui.selected.size
              ? `已选择 ${editor.ui.selected.size} 个主题`
              : "让思绪，自然展开"}
          </span>{" "}
          <span />
        </div>
      </main>
      <div className="bottom-hint">
        <span>Enter 新建主题</span>
        <i />
        <span>Tab 调整层级</span>
        <button onClick={() => setHelp(true)} title="快捷键帮助">
          <Keyboard size={15} />
        </button>
      </div>
      {bubble && editor && (
        <div
          className="floating-format"
          style={{ left: bubble.x, top: bubble.y }}
        >
          <FormatBar editor={editor} />
        </div>
      )}
      {help && (
        <div
          className="modal-backdrop"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) setHelp(false);
          }}
        >
          <section
            className="dialog help-dialog"
            role="dialog"
            aria-modal="true"
            aria-label="快捷键"
          >
            <div className="dialog-header">
              <div>
                <h2>让思考更流畅</h2>
                <p>常用快捷键</p>
              </div>
              <IconButton
                label="关闭快捷键"
                icon={X}
                onClick={() => setHelp(false)}
              />
            </div>
            <div className="shortcut-list">
              {shortcuts.map(([label, key]) => (
                <div key={label}>
                  <span>{label}</span>
                  <kbd>{key}</kbd>
                </div>
              ))}
            </div>
            <div className="help-footer">
              <span>拖动圆点移动主题，向右拖动成为子主题。</span>
              <span>浏览器占用的快捷键可通过主题菜单操作。</span>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
