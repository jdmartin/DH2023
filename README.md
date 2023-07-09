# dh-host-sec-2023
Survey of DH servers and their security issues.

## N.B:

For materials related to the presentation in Graz, please see the folder `graz-2023`.

  - Visualizations are in `graz-2023/viz` and are grouped by ADHO or DHQ.
  - Our presentation is available [here](https://drive.google.com/drive/folders/1N9G0un89vXmzq34f_-dAfcJXJfNoorku) via Google Drive. It is a keynote presentation.
  - The Wiki referenced in our talk lives [here](https://wiki.dhlinux.org/), and its source code lives [here](https://github.com/jdmartin/dhlinux-jekyll).

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
