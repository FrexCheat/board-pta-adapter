# board-gplt-fetcher

## Use Docker

🎯TODO ... ...

## Use manually

### Setup environment

- Install [uv](https://docs.astral.sh/uv/) (Python version manager)

- Init this project with uv

```shell
cd your_project_root_dir
uv sync
```

### Setup config

- Rename `config.example.yml` to `config.yml`

- Update your `config.yml` like below:

```yml
# output dir of generator and sync result
output_dir: ./output

fetcher:
  pta_session: your_pta_session_cookie_here
  problem_set_id: "your_problem_set_id_here"

# pass mark for level 1 and level 2
contest:
  standard_1: 800
  standard_2: 400

# excel file info (path, name and sheet name) for generator
generator:
  excel_dir: ./xlsx
  excel_name: "data.xlsx"
  sheet_name: "origin"

# sync interval in seconds
sync_interval: 15
```

### Generate Static Info (contest, students, teams)

- Prepare your excel file according to `template.xlsx` in `xlsx` folder

- Put your excel file in the `xlsx` folder named as `data.xlsx` (you can change the name in config)

- Run the generator script

```shell
uv run gen
```

- The generated static info will be in the `output` folder (you can change the folder in config)

### Syncing Ranking Info from PTA

- Run the sync script

```shell
# this script will fetch ranking info from PTA
# and update the result in the output folder periodically
# according to the `sync_interval` setting in config.yml
uv run sync
```
