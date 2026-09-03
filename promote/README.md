# promote/

Posting tooling for the personal X account (@hnagar_dev). Not part of the site.

    cp .env.example .env         # then paste the four X keys into .env
    python promote.py launch_thread.txt          # dry run (nothing posted)
    python promote.py launch_thread.txt --send   # posts the thread

Threads are plain text files; tweets are separated by a line containing only `---`.
