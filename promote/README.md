# promote/

Posting tooling for the personal X account (@hnagar_dev). Not part of the site.

    cp .env.example .env         # then paste the four X keys into .env
    python promote.py launch_thread.txt          # dry run (nothing posted)
    python promote.py launch_thread.txt --send   # posts the thread

Threads are plain text files; tweets are separated by a line containing only `---`.

Posting through the API now requires a paid credit balance on the X developer
account; without it the API returns 402 "credits depleted". The dry run still
works and is the quickest way to get the tweets for posting by hand.
