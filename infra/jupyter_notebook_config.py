# Configuration file for jupyter-notebook.
# copy this to ~/.jupyter

## The IP address the notebook server will listen on.
c.NotebookApp.ip = '0.0.0.0'

c.NotebookApp.open_browser = False

#  The string should be of the form type:salt:hashed-password.
c.NotebookApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$WkwlnBjS+qB7d4yEOUPe/Q$aJh1vq4OrB5Hfeb+7mXbUGuqQa1kyMWuq2fhfs3AX3Y'

## The port the notebook server will listen on.
c.NotebookApp.port = 8888

# open Jupyterlab in collaborative mode
c.LabApp.collaborative = True

