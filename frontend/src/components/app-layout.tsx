import { ReactNode } from "react";

// Generic chat + side-panel layout. The chat fills the screen; tap the
// top-right button to slide the panel in. Desktop renders inline at 2fr/1fr,
// mobile renders as a slide-over drawer with a backdrop.

type AppLayoutProps = {
  chat: ReactNode;
  panel: (onClose: () => void) => ReactNode;
  panelTitle: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function AppLayout({ chat, panel, panelTitle, open, onOpenChange }: AppLayoutProps) {
  const toggle = (next: boolean) => onOpenChange(next);

  return (
    <main className="h-screen relative">
      {!open && (
        <button
          className="fixed top-3 right-3 z-50 bg-red-400 text-white rounded-xl px-3.5 py-2 text-sm font-medium cursor-pointer hover:bg-red-500 transition-colors"
          onClick={() => toggle(true)}
          type="button"
        >
          {panelTitle}
        </button>
      )}

      <div className={`grid h-full grid-cols-1 ${open ? "md:grid-cols-[2fr_1fr]" : ""}`}>
        <div className="flex flex-col min-h-0">{chat}</div>

        {open && (
          <aside className="hidden md:flex flex-col flex-1 border-l border-zinc-300 bg-zinc-50/50 overflow-y-auto px-5 py-4">
            {panel(() => toggle(false))}
          </aside>
        )}
      </div>

      {open && (
        <>
          <div
            className="md:hidden fixed inset-0 bg-black/20 z-40 cursor-pointer"
            onClick={() => toggle(false)}
          />
          <aside className="md:hidden fixed inset-y-0 right-0 z-50 w-[85vw] max-w-sm bg-white border-l border-zinc-300 shadow-xl flex flex-col overflow-y-auto px-5 py-4">
            {panel(() => toggle(false))}
          </aside>
        </>
      )}
    </main>
  );
}
