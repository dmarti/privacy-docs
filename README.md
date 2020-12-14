# privacy-docs
Privacy documents


## Building agent permission letters

You will need to have Docker installed and running. All other dependencies are in the Dockerfile.

 * Run the command: `./build.sh`

 * PDF will be named as a number (using the NationBuilder ID)

 * Email address will be written at the top of the PDF, beneath the snail mail address

 * (Line above user name  is where Docusign signature widget goes)

 * Opt-out letters are created as `.txt` under oos

This is done with pretty basic template processsing with 
Pandoc.

The `extract-csv.py` script parses out the CSV from NationBuilder, and invokes the "mo"
utility to put required values into the right spots on the template.

All the commands used are in the Makefile.




## References

[Final Text of Regulations - Title 11. Law - Division 1. Attorney General - Chapter 20. California Consumer Privacy Act Regulations - oal-sub-final-text-of-regs.pdf](https://www.oag.ca.gov/sites/all/files/agweb/pdfs/privacy/oal-sub-final-text-of-regs.pdf#page=1&zoom=auto,-121,798)
