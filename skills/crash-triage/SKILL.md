---
name: crash-triage
description: Diagnose an Xcode/iOS crash log or stack trace to a root-cause hypothesis and file:line without a full-project read.
---

1. If frames show raw addresses, not symbols, say so and stop — ask for a symbolicated export or the `atos` command. Do not guess at unsymbolicated frames.
2. Walk the crashing thread top-down; stop at the first frame in the user's own module (skip libswiftCore, UIKitCore, libobjc, libdispatch, Foundation, SwiftUI internals — note as skipped).
3. Classify first: `SIGABRT` + "Unexpectedly found nil" -> force unwrap; + "Index out of range" -> bounds; `EXC_BAD_ACCESS` -> use-after-free/unsafe pointer/data race; `EXC_BREAKPOINT`/`SIGTRAP` -> runtime trap; NSException -> bad cast/KVC key; watchdog (0x8badf00d) -> main thread blocked at launch/transition, not a traditional crash.
4. Read only the crashing function (`rg -n "func <name>"`) plus its caller if the crashing value is passed in — not the file, not the module.
5. Check: force unwrap on a legitimately-nilable value, off-main-thread mutation, a closure capturing `self` strongly across an async gap, Core Data used across contexts, unchecked `Task` cancellation.
6. Output: 2-4 sentence hypothesis, `file:line`, and a fix or the concrete thing to verify. Reference frame numbers, never paste the full trace.
