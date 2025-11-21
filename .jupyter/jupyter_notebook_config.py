# Jupyter Notebook Configuration
# This prevents Jupyter from creating checkpoint folders

c = get_config()  # noqa

# Disable checkpoints completely by setting to an empty implementation
c.FileContentsManager.checkpoints_class = 'notebook.services.contents.checkpoints.NoOpCheckpoints'

# As a backup, redirect to a hidden location outside your working directories
c.FileCheckpoints.checkpoint_dir = '/tmp/jupyter_checkpoints'
