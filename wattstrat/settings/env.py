# Use 12factor inspired environment variables or from a file
import environ
from wattstrat.settings.components.dir import SETTINGS_DIR

env = environ.Env()

# Ideally move env file should be outside the git repo
# i.e. BASE_DIR.parent
env_file = SETTINGS_DIR / 'local.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))