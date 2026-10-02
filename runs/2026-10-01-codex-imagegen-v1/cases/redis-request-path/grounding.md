# Source grounding

Read only this case prompt.md and src/**. Source pin: src/PINNED.txt:1–5, Redis 8.10.2, commit 498ecd0d6d007db11ddb3aea9428552598a78622.

- Main listener registered on server.el: src/src/server.c:2835–2839; main loop:8410. Accept creates client and invokes callback: src/src/networking.c:1709,1732; callback assigns I/O thread:1663.
- Fewest-client assignment, initial unbind, disabled I/O: src/src/iothread.c:334–360. Initial queue list join and notifier:503–515.
- Worker takes queued client and binds its event loop only if absent, enabling I/O: src/src/iothread.c:776–816.
- Read into querybuf: src/src/networking.c:3989; parse:4045. Inline and multibulk branches and incomplete handling:3749–3777. Worker marks complete command and yields, never executes:3840–3846.
- Yield disables I/O without normal unbind and moves client node: src/src/iothread.c:115–136; main pending queue join and conditional notification:31–47.
- Main drains queue, switches running_tid, dispatches pending command: src/src/iothread.c:603–670; command execution and subsequent buffered input: src/src/networking.c:3555–3603.
- Return clears pending write membership, restores running_tid and queues client: src/src/iothread.c:694–712; mutex transfer and notification:567–590.
- Reply flush and residual writable handler: src/src/iothread.c:808–839; writable callback invokes writeToClient: src/src/networking.c:2949–2951.
- Special clients remain main: src/src/iothread.c:292–299,683–687. AOF always return delayed:571–574. Main beforeSleep servicing: src/src/server.c:2079–2111.

Diagram scope is an ordinary successfully accepted non-blocking client, not replication, connection rejection, or blocked command paths. Source line references are included in the image.
