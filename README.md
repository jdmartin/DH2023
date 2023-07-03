# dh-host-sec-2023
Survey of DH servers and their security issues.

## N.B:

For materials related to the presentation in Graz, please see the folder `graz-2023`.

  - Visualizations are in `graz-2023/viz` and are grouped by ADHO or DHQ.
  - Slides are in `graz-2023/slides`. (Note: voiceover is used in the slides, if using keynote use "play recorded" rather than just "play.")

## Usage:

If you want to start completely from the beginning:

0. Create your virtualenv
1. Run either `poetry install` or `pip install -r requirements.txt`
2. Copy .env_dist to .env
3. Add the necessary keys
4. Run `start_over.sh`.

If you want to explore the databases:

1. Run `python scripts/explore-db.py`.

If you want to check the gathered data against some threat lists:

1. Run `get_threat_lists.sh`
2. Run `python scripts/check_threat_lists.py`

(Note: Eventually, this threat analysis will be integrated into the db.)
