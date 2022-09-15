Request object visibility output from [STARALT](http://catserver.ing.iac.es/staralt/) via Python scripts.

## About STARALT
> Staralt is a program that shows the observability of objects in various ways: either you can plot altitude against time for a particular night (*Staralt*), or plot the path of your objects across the sky for a particular night (*Startrack*), or plot how altitude changes over a year (*Starobs*), or get a table with the best observing date for each object (*Starmult*).

For more details please refer to [the help page](http://catserver.ing.iac.es/staralt/staralt_help.html) of STARALT.

---
## About the scripts

The STARALT request is generated by `staralt.py`. Theoretically, the script allows requests to be made identically to the web page. Yet some of the values are set to default (e.g. the observatory name) to fit my own need. Please modify the script accordingly to suit whatever needs.
`query.py` provides an instant that requests visibility for a table of cluster stars.

Future ToDo ~~🐦~~

- date validation (to avoid dates like Feb. 30th)
  
- perform requests with preset configuration (maybe a JSON file or anything similar)