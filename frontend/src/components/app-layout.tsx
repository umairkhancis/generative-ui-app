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
          className="fixed top-3 right-3 z-50 w-11 h-11 flex items-center justify-center rounded-full bg-[#EB6030] text-white shadow-md cursor-pointer hover:bg-[#d04f24] transition-colors"
          onClick={() => toggle(true)}
          type="button"
          aria-label={`Open ${panelTitle}`}
          title={panelTitle}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
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
