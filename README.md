# Cascade

Copies e-mails between IMAP servers. Works for migrating / copying e-mails between gmail accounts.

## Configuration File

cascade will look for ```cascade.conf``` under home folder. You can also pass it on the command line.

```
[Source]
server: imap.gmail.com
username: me@gmail.com
password: xyz
folder: "[Gmail]/All Mail"

[Destination]
server: imap.gmail.com
username: me@myapps.com
password: xyz
folder: "Copied"

[Dates]
after: 1-Apr-2004
before: 29-Dec-2014
```

## Copy e-mails

When you create the configuration file under your home folder, run this;
```
cascade -c
```

## Help

```
cascade -h
```