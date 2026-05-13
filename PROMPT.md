# Talabat Generative UI Demo — Planning Prompt

## Goal

Demonstrate this project's generative UI capabilities for **Talabat** (a food delivery company), framed around a coherent **order placement journey**. The output is a planning conversation first, then incremental implementation — capability by capability.

## Capabilities to demonstrate

1. **Controlled generative UI** — agent renders UI the developer has wired up explicitly.
2. **Fixed-schema declarative generative UI** — agent emits structured data that maps to predefined components (e.g. card carousel, details card).
3. **MCP app / open-ended generative UI** — agent renders novel UI on the fly via MCP.
4. **Canvas app** — a persistent, stateful surface (like the existing Todo app) the user interacts with directly while the agent collaborates.

The demo does **not** need a 1:1 mapping between capabilities and journey steps. What matters is that all four capabilities are showcased, and that the overall experience tells one coherent food-delivery story.

## Domain adaptation

Replace the current flights domain with food delivery:

- **Flights data** → mock data for **restaurants** and **menu items**.
- **Flight search tools** → tools for **restaurant discovery** and **menu item discovery**.
- **Flights schema** →
  - Restaurants → **card carousel**
  - Menu items → **card carousel**
  - Item detail → **details card**
  - Cart Management Capability → **python function as a tool call which increments and decrements the items selected and shows what is the state of the cart and mock like a typical standard cart service**
  - Order Summary → **summary card**
  - Place an Order Confirmation → **Place an Order Confirmation**
  - Order Tracking → **Order Tracking States (Confirming, Preparing, Delivering, Delivered) Progression Card with ETA and order summary**

## Brand

- Primary color: `#EB6030`
- Icons / logos:
  - `/Users/umairahmed.khan/Downloads/images.png`
  - `/Users/umairahmed.khan/Downloads/logo.jpg`

## Constraints

- **Do not modify core framework / infra code.** Only change the parts that need to be adapted to the food-delivery domain (mock data, tool definitions, schemas, component content, copy, theming).
- **No implementation before alignment.** Until we agree on what an effective demonstration looks like for each capability, keep this as a high-level plan.
- **Work in slices.** Progress one capability at a time. For each, we discuss:
  - *What is the ideal way to demonstrate this capability for food delivery?*
  - *Which step(s) of the order placement journey does it best fit?*
  - Then implement, review, and move to the next.

## How I'd like you to work with me

1. Start by proposing, for each of the four capabilities, the **ideal demonstration** within the food-delivery / order-placement use case — including which journey step it maps to and why.
2. Surface trade-offs and ask clarifying questions where the choice isn't obvious.
3. Wait for my agreement on the plan for a given capability before implementing it.
4. Implement one capability at a time, then we review together before moving on.
