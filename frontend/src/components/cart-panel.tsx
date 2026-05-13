// CartPanel — the side-panel "canvas" rendering of the cart.
//
// Reads shared state (`agent.state.cart`) through props from App.tsx and
// writes back via `onUpdate`. Same source of truth as the inline
// cartSummaryCard (controlled GenUI) and backend `Command(update={cart})`.
import { parsePrice, setQuantity, type Cart } from "@/lib/cart";

const BRAND = "#EB6030";

type CartPanelProps = {
  cart: Cart | undefined | null;
  onUpdate: (cart: Cart) => void;
  onCheckout: () => void;
  isRunning: boolean;
  onClose?: () => void;
};

export function CartPanel({ cart, onUpdate, onCheckout, isRunning, onClose }: CartPanelProps) {
  const items = cart?.items ?? [];
  const hasItems = items.length > 0;

  const bump = (itemId: string, delta: number) => {
    if (isRunning || !cart) return;
    const current = items.find((i) => i.id === itemId);
    const next = (current?.quantity ?? 0) + delta;
    onUpdate(setQuantity(cart, itemId, next));
  };

  const clearAll = () => {
    if (!cart) return;
    onUpdate({
      restaurant_id: null,
      restaurant: null,
      items: [],
      subtotal: "AED 0",
      delivery_fee: "Free",
      total: "AED 0",
      item_count: 0,
    });
  };

  return (
    <div className="flex flex-1 flex-col">
      <div
        className="flex items-center gap-2 mb-3 pb-3 border-b"
        style={{ borderColor: "#fdd8c5" }}
      >
        <span className="text-sm font-medium tracking-wider" style={{ color: BRAND }}>
          Cart
        </span>
        {hasItems && (
          <span className="text-[11px] text-gray-500">{cart?.restaurant ?? ""}</span>
        )}
        <div className="flex items-center gap-1 ml-auto">
          {hasItems && (
            <button
              className="cursor-pointer inline-flex items-center justify-center rounded-md bg-orange-50 text-orange-500 hover:bg-orange-100 hover:text-orange-700 h-7 px-2 text-[11px] font-medium transition-colors disabled:opacity-40 disabled:cursor-default"
              onClick={clearAll}
              disabled={isRunning}
              type="button"
              aria-label="Clear cart"
            >
              Clear
            </button>
          )}
          {onClose && (
            <button
              className="cursor-pointer inline-flex items-center justify-center rounded-md bg-orange-50 text-orange-500 hover:bg-orange-100 hover:text-orange-700 h-7 w-7 transition-colors"
              onClick={onClose}
              type="button"
              aria-label="Close panel"
            >
              <svg width="14" height="14" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"/>
              </svg>
            </button>
          )}
        </div>
      </div>

      {!hasItems ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-sm text-zinc-400 px-4 text-center">
          <svg className="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          Your cart is empty.
          <span className="text-xs text-zinc-400">
            Browse restaurants or ask the assistant to find something for you.
          </span>
        </div>
      ) : (
        <>
          <ul className="list-none m-0 p-0 flex flex-col gap-1.5 overflow-y-auto">
            {items.map((item) => {
              const qty = item.quantity ?? 0;
              const line = item.line_total ?? `AED ${Math.round(parsePrice(item.price) * qty)}`;
              return (
                <li
                  key={item.id}
                  className="rounded-lg border border-zinc-200 bg-white px-3 py-2.5 flex items-center gap-3"
                >
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      type="button"
                      onClick={() => bump(item.id, -1)}
                      disabled={isRunning}
                      aria-label={`Decrease ${item.name}`}
                      className="w-6 h-6 rounded-full border border-gray-300 text-gray-700 flex items-center justify-center hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M20 12H4" />
                      </svg>
                    </button>
                    <span className="text-[12px] font-bold w-6 text-center" style={{ color: BRAND }}>
                      {qty}
                    </span>
                    <button
                      type="button"
                      onClick={() => bump(item.id, 1)}
                      disabled={isRunning}
                      aria-label={`Increase ${item.name}`}
                      className="w-6 h-6 rounded-full text-white flex items-center justify-center disabled:cursor-not-allowed disabled:opacity-50"
                      style={{ backgroundColor: BRAND }}
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="3" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-sm text-zinc-900 truncate">{item.name}</div>
                    <div className="text-[11px] text-zinc-400">
                      {qty} × {item.price}
                    </div>
                  </div>
                  <div className="text-sm font-semibold text-zinc-900 whitespace-nowrap">{line}</div>
                </li>
              );
            })}
          </ul>

          <div className="mt-auto pt-4 border-t border-zinc-200 space-y-1.5 text-sm">
            <div className="flex items-center justify-between text-zinc-600">
              <span>Subtotal</span>
              <span>{cart?.subtotal ?? "—"}</span>
            </div>
            <div className="flex items-center justify-between text-zinc-600">
              <span>Delivery</span>
              <span>{cart?.delivery_fee ?? "—"}</span>
            </div>
            <div className="flex items-center justify-between pt-1.5 border-t border-zinc-200">
              <span className="font-semibold text-zinc-900">Total</span>
              <span className="font-bold text-zinc-900">{cart?.total ?? "—"}</span>
            </div>
            <button
              type="button"
              onClick={onCheckout}
              disabled={isRunning}
              className="w-full mt-2 py-2 rounded-lg text-sm font-semibold text-white transition-colors disabled:cursor-not-allowed disabled:opacity-50"
              style={{ backgroundColor: BRAND }}
            >
              Place Order
            </button>
          </div>
        </>
      )}
    </div>
  );
}
