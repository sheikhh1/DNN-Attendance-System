from website import create_app
import os
from website.utility_functions import shot_folder_manager

import torch, gc
gc.collect()
torch.cuda.empty_cache()

app = create_app()

app.app_context().push()

shot_folder_manager()
    
if __name__ == '__main__':
    print(os.getcwd())
    app.run(debug=True, use_reloader=False)
