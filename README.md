# Vaccine Availability Alerts
With the difficulty of getting registration slots for the COVID19 vaccine, this repository aims to check availability of vaccination slots at CVS and RiteAid. The Lambda function takes as its event payload a configuration that includes the stores that it should check. CVS is a static configuration but RiteAid requires the entry of particular store locations that are queried.

## Configuration
Each of the template configuration files need to be copied and then updated accordingly.

```
etc/template_config.json -> etc/config.json
etc/template_environment.sh -> etc/environment.sh
etc/template_event.json -> event.json
```

The `config.json` file needs to be updated with the RiteAid store location numbers and addresses.
The `environment.sh` file needs to be updated with appropriate files for use with `make`.
The `event.json` file is used for testing, is the same schema as `config.json`, and can be reduced based on the required testing.

## Execution
The `makefile` has all of the required commands for deploying and testing. Ensure that `etc/environment.sh` is properly configured.

## Attribution
Thanks to [@dmachine](https://github.com/dmachine) for initially finding the APIs and getting this project kicked off.
