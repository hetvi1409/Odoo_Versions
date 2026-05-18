
from . import models

def post_init_hook(env):
    folder = env.ref('documents.document_finance_folder', raise_if_not_found=False)
    if folder:
        folder.name = "5 Finance"