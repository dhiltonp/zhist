## ZFS History - simplified usage of ZFS snapshots ##

The purpose of zhist is to simplify access to past ZFS snapshots.  For example, if you "zhist ls somefile" then the results will be:  A list of all the previous snapshot versions of that file or directory.  No need to find the right .zfs directory, or check to see which ones have changed.  Some reasonable steps (stat) are taken inside this zhist, to identify the previous snaps, and to identify unique snaps of the requested object.

There is a long way still remaining to go.  But this is a 90/10 rule.  The first "good enough for usage" version is available, and that's what most people would care about.

You can get the present release as follows:
```
svn export https://zhist.googlecode.com/svn/tags/0.6beta
sudo chown root:root 0.6beta/zhist
sudo chmod 755 0.6beta/zhist
(optionally, edit the first line of 0.6beta/zhist to match your environment’s preferred python location)
sudo mv 0.6beta/zhist /usr/local/bin
```

## EXAMPLE ##

(In this example, I have a "timestamp.txt" file which I update every minute via cron.  Therefore, this file has changed in every snapshot since creation.

```
[username@machinename ~\]$ zhist ls timestamp.txt
/tank/home/username/timestamp.txt
/tank/.zfs/snapshot/frequent-2010-05-18-23-45-00/home/username/timestamp.txt
/tank/.zfs/snapshot/frequent-2010-05-18-23-30-00/home/username/timestamp.txt
/tank/.zfs/snapshot/frequent-2010-05-18-23-15-00/home/username/timestamp.txt
/tank/.zfs/snapshot/hourly-2010-05-18-23-00-00/home/username/timestamp.txt
/tank/.zfs/snapshot/hourly-2010-05-18-22-00-00/home/username/timestamp.txt
/tank/.zfs/snapshot/hourly-2010-05-18-21-00-00/home/username/timestamp.txt
  (...)
```

## If you would like to participate: ##
  * If you have a google account, join the "zhist-discuss" google group.
  * If you don't have a google account,
    * Send email to zhist-discuss+subscribe@googlegroups.com
    * You'll get a confirmation message, which you'll have to confirm.
    * And then you'll be able to send mail to zhist-discuss@googlegroups.com