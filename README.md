# zillow_scraper
Simple scraper to get text value of zillow listings

## Schedule the job using launchd
- For some reason, crontab doesn't work with keyring in mac [issue](https://github.com/jaraco/keyring/issues/188)
- Use launchd with below steps
```
# copy the plist to launchd directory
cp zillow.scraper.plist ~/Library/LaunchAgents/

# load and start the job
launchctl load ~/Library/LaunchAgents/zillow.scraper.plist
launchctl start zillow.scraper.plist

# verify the job has been started
launchctl list | grep zillow
```