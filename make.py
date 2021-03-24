import click
import subprocess

DB_NAME = "dbname"
DB_PASS = "dbpass"
DB_USER = "dbuser"

DB_ENGINES = {
    "mysql": ["5.6", "5.7", "8", "latest"],
    "postgres": ["9.5", "9.6", "10", "11", "12", "13", "latest"],
}

PYTHON_VERSIONS = ["3.6", "3.7", "3.8", "3.9"]

DEBUG_COLOR = "yellow"
INFO_COLOR = "green"
ERROR_COLOR = "red"

DEBUG = False


def log_debug(message):
    global DEBUG
    if DEBUG:
        click.secho(message=message, fg=DEBUG_COLOR)


def log_info(message):
    click.secho(message=message)


def log_error(message):
    click.secho(message=message, fg=ERROR_COLOR)


def make_env(
    python_version,
    db_engine,
    db_version,
    db_name=DB_NAME,
    db_pass=DB_PASS,
    db_user=DB_USER,
):
    return {key.upper(): value if value else "" for key, value in locals().items()}


# MAKE_BUILD_CMD = docker-compose -f docker-compose-$(DB_ENGINE).yml build --parallel db test
# MAKE_TEST_RUN  = docker-compose -f docker-compose-$(DB_ENGINE).yml run test pytest .


def get_info_str(env):
    return f"{env['DB_ENGINE']}:{env['DB_VERSION']} PYTHON:{env['PYTHON_VERSION']}"


def run_cmd(cmd, env):
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def run_test(env):
    resp = build_docker(env)
    if resp.returncode != 0:
        return resp, env

    global DEBUG

    log_info(f"Running tests for: {get_info_str(env)}")

    cmd = [
        "docker-compose",
        "-f",
        "docker-compose-{DB_ENGINE}.yml".format(**env),
        "run",
    ]
    services = ["test", "pytest", "."]
    cmd = cmd + services

    log_debug(f"Running command {cmd}")

    if DEBUG:
        env_str = " ".join(f"{key}={value}" for key, value in env.items())
        cmd_str = " ".join(cmd)
        log_debug(f"{env_str} {cmd_str}")

    return run_cmd(cmd, env), env


def build_docker(env):
    log_info(f"Building docker for: {get_info_str(env)}")

    global DEBUG
    cmd = [
        "docker-compose",
        "-f",
        "docker-compose-{DB_ENGINE}.yml".format(**env),
        "build",
        "--parallel",
    ]
    services = ["db", "test"]
    if DEBUG:
        cmd = cmd + services
    else:
        cmd = cmd + ["-q"] + services

    log_debug(f"Running command {cmd}")

    if DEBUG:
        env_str = " ".join(f"{key}={value}" for key, value in env.items())
        cmd_str = " ".join(cmd)
        log_debug(f"{env_str} {cmd_str}")

    return run_cmd(cmd, env)


@click.group()
@click.option("--debug/--no-debug", default=False)
def commands(debug):
    global DEBUG
    DEBUG = debug


@click.command()
@click.option("--db-version", required=False, default="all")
@click.option("--db-engine", required=False, default="all")
@click.option("--python-version", required=False, default="all")
@click.option("--debug/--no-debug")
@click.option("--omit-latest", required=False, default=True)
def test(omit_latest, debug, python_version, db_engine, db_version):
    """Run tests."""
    global DEBUG
    DEBUG = DEBUG or debug

    db_engines_str = ", ".join(DB_ENGINES.keys())
    if db_engine == "all":
        db_engines = list(DB_ENGINES.keys())
        log_info(f"Running tests for engines: {db_engines_str}")
        if db_version:
            db_version = None
            log_debug(
                "Ignoring given db_version argument, using all possible versions."
            )
    else:
        db_engines = [db_engine]
        if db_engine not in DB_ENGINES:
            log_error(
                f"The given option {db_engine} is not right. The list of supported engines is: {db_engines_str}"
            )
            exit(1)

    if python_version == "all":
        python_versions = PYTHON_VERSIONS
    else:
        python_versions = [python_version]

    responses = []
    for dbengine in db_engines:

        if db_version is None or db_version == "all":
            dbversions = DB_ENGINES[dbengine]
            if omit_latest:
                dbversions.remove("latest")
        else:
            dbversions = [db_version]

        for dbversion in dbversions:
            for python_version in python_versions:

                env = make_env(
                    python_version=python_version,
                    db_engine=dbengine,
                    db_version=dbversion,
                )
                log_debug(f"Using env: {env}")
                responses += [run_test(env)]

    ok_msg = click.style("OK", fg="green")
    err_msg = click.style("ERROR", fg="red")
    for res, env in responses:
        use_msg = ok_msg if res.returncode == 0 else err_msg
        if res.returncode == 0:
            print(get_info_str(env) + " " + use_msg)
        else:
            print(get_info_str(env) + " " + use_msg)

    for res, env in responses:
        if res.returncode == 0:
            continue

        log_error("-" * 80)
        log_error("-" * 37 + " START " + "-" * 36)
        log_error("  " + get_info_str(env))
        log_error("-" * 80)
        print(res.stderr)
        print(res.stdout)
        log_error("-" * 38 + " END " + "-" * 37)
        log_error("  " + get_info_str(env))
        log_error("-" * 80)


commands.add_command(test)

if __name__ == "__main__":
    commands()
