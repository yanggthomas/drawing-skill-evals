Use case: infographic-diagram
Create one original polished technical diagram as a raster PNG, landscape 1800x1400 or larger, white background, high legibility. Title: "Redis 8.10.2 — life of a client request". Subtitle: "io-threads > 1 • ordinary, non-blocking client • time flows downward". Two clearly separated vertical lanes: MAIN THREAD (thread 0) on left, ASSIGNED I/O THREAD (thread i) on right. Use calm blue for main, teal for I/O, orange for cross-thread handoffs. Black readable text. Compact rounded boxes, plenty of whitespace, precise directional arrows. Include numbered phases, with connections strictly in order 1 → 2 → 3 → 4 → 5 → 6. No decorative imagery.

Top-left phase 1: "ACCEPT & ASSIGN"
"acceptCommonHandler → createClient"
"clientAcceptHandler → assignClientToIOThread"
"Choose the I/O thread with fewest clients"
"Unbind main event loop; disable client read/write"
small reference "networking.c:1663,1709,1732 • iothread.c:334–360"

Cross-lane arrow 1 to 2 rightwards, labeled "client handoff: mainThreadPendingClientsToIOThreads[i] → t->pending_clients"
secondary short label "mutex-protected list join + event notifier • iothread.c:503–515"

Upper-right phase 2: "ATTACH TO I/O EVENT LOOP"
"processClientsFromMainThread"
"Enable read/write; bind t->el once"
"Install readQueryFromClient"
reference "iothread.c:776–816"
Downward arrow to right phase 3.

Right phase 3: "READ & PARSE QUERY"
"readQueryFromClient → clientConnRead"
"processInputBuffer → inline / multibulk parser"
"Complete command: CLIENT_IO_PENDING_COMMAND"
"enqueuePendingClientsToMainThread(c, 0)"
reference "networking.c:3989,4045,3749–3777,3840–3846"
A small side note next to this phase: "Incomplete input: keep reading on I/O thread".
Cross-lane arrow from phase 3 to phase 4 leftwards, with orange label:
"Disable client read/write; retain I/O event-loop binding"
"t->pending_clients_to_main_thread → mainThreadPendingClients[i]"
"mutex-protected list join; notify main if needed"
reference "iothread.c:115–136,31–47"

Middle-lower-left phase 4: "EXECUTE COMMAND"
"processClientsFromIOThread"
"running_tid = MAIN; set CLIENT_PENDING_COMMAND"
"processPendingCommandAndInputBuffer"
"→ processCommandAndResetClient → processCommand"
"Execute command; accumulate reply in client buffers"
reference "iothread.c:603–670 • networking.c:3555–3603"
Important note inside this box: "I/O thread never executes the command."

Lower-left phase 5: "RETURN CLIENT"
"running_tid = c->tid"
"Queue on mainThreadPendingClientsToIOThreads[i]"
reference "iothread.c:694–712"
Down arrow from phase 4 to 5. Cross-lane arrow from 5 to 6 rightwards:
"mutex-protected handoff → t->pending_clients"
"event notifier when needed; beforeSleep also drains queues"
reference "iothread.c:567–590 • server.c:2079–2111"

Lower-right phase 6: "WRITE REPLY"
"processClientsFromMainThread"
"Re-enable read/write → writeToClient"
"If bytes remain: install sendReplyToClient"
"Writable event → writeToClient again"
reference "iothread.c:808–831 • networking.c:2949–2951"
Small outgoing arrow to an external pill "Reply to client socket".
Small note below: "Connection stays assigned to I/O thread for the next request."

Bottom band with two concise annotations:
"Ownership safety: the shared client is queued between threads; read/write flags prevent concurrent I/O during main-thread processing."
"Scope: special clients may stay on main (e.g. blocked, Pub/Sub, tracking). AOF appendfsync=always delays return until after flush/fsync."
references "iothread.c:132–136,292–299,571–574,683–687"
Footer small but clear: "Source: Redis tag 8.10.2 • commit 498ecd0d6d007db11ddb3aea9428552598a78622 • references are src/ file:line"

Avoid: no old Redis global batch-worker design, no worker executing command, no thread rebinding on every request, no invented components, no crossing arrows, no obscured text. Render all labels legibly; function names and queue names exactly as given.