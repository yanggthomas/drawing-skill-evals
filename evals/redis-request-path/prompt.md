---
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

I'm trying to understand how Redis 8 handles a client request when I/O threads are enabled (`io-threads` greater than 1). The Redis source, pinned at the tag and commit in `PINNED.txt`, is in the read-only source directory available to this session. Draw one diagram that explains the life of one request across the main thread and an I/O thread: which thread accepts the connection, which reads and parses the query, which executes the command, which writes the reply, and how the client is handed between threads. Ground every element in the code. Save the finished diagram as a PNG image at `out/request-path.png`.
