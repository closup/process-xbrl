## SpecStory

## explain how arelle works in this code base (8/22/2024, 2:05:19 PM)

_**User**_



---

_**Assistant**_

Based on the provided code and context, Arelle is being used as a dependency in this project for XBRL (eXtensible Business Reporting Language) processing. Here's an explanation of how Arelle is integrated and used in this codebase:

1. Arelle Integration:
   The project includes Arelle as a submodule in the dependencies directory, as seen in the `.gitmodules` file:


```1:7:.gitmodules
[submodule "Arelle"]
	path = dependencies/Arelle
	url = https://github.com/Arelle/Arelle.git
[submodule "ixbrl-viewer"]
	path = dependencies/ixbrl-viewer
	url = https://github.com/Arelle/ixbrl-viewer

```


2. System Path Configuration:
   In the `xbrl_processing.py` file, the code adds Arelle to the system path to make its imports possible:


```19:26:app/utils/xbrl_processing.py
# Make arelle imports possible
base_dir = os.path.abspath(nth_parent_dir(__file__, 3))
# Add the base directory to the sys.path
sys.path.append(base_dir)
# Also add the Arelle.arelle directory inside dependencies 
arelle_dir = os.path.join(base_dir, "dependencies", "Arelle")
sys.path.append(arelle_dir)
from arelle import CntlrCmdLine
```


3. Arelle Imports:
   After adding Arelle to the system path, the code imports specific Arelle modules:


```26:27:app/utils/xbrl_processing.py
from arelle import CntlrCmdLine
from arelle.Locale import setApplicationLocale
```


4. XBRL Processing:
   The `create_viewer_html` function in `xbrl_processing.py` uses Arelle's functionality to create an interactive XBRL viewer:


```50:117:app/utils/xbrl_processing.py
def create_viewer_html(output_file : str,
                       viewer_outpath : str):
    """
    Runs Arelle and ixbrl-viewer submodules to create a viewer html and 
    accompanying javascript file.
    """
    viewer_filepath = os.path.join(ROOT, viewer_outpath, 'viewer.html')

    # command to run Arelle process
    plugins = os.path.join(ROOT, "dependencies", "ixbrl-viewer", "iXBRLViewerPlugin")
    viewer_url = "https://cdn.jsdelivr.net/npm/ixbrl-viewer@1.4.8/iXBRLViewerPlugin/viewer/dist/ixbrlviewer.js"

    print('viewer path', viewer_filepath)
    args = f"--plugins={plugins} -f {output_file} --save-viewer {viewer_filepath} --viewer-url {viewer_url}"
    
    args = shlex.split(args)
    setApplicationLocale()
    gettext.install("arelle")
    print("Validating XBRL...")
    CntlrCmdLine.parseAndRun(args)

    # Read in the generated HTML
    print("Creating interactive viewer...")
    try:
        with open(viewer_filepath, 'r', encoding="utf8") as file:
            html_content = file.read()
        print("HTML content read successfully")
    except Exception as e:
        print(f"Error reading HTML file: {str(e)}")
        return

    # Parse the HTML with BeautifulSoup
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        print("HTML parsed successfully")
    except Exception as e:
        print(f"Error parsing HTML: {str(e)}")
        return

    # Find the script tag we wish to modify
    script_tag = soup.find('script', {'src': 'ixbrlviewer.js'})
    if script_tag:
        # Update the src attribute
        script_tag['src'] = url_for('static', filename='js/ixbrlviewer.js')
        print("Script tag updated")
    else:
        print("Script tag not found")

    # Write the modified HTML back out
    print("Writing modified HTML file...")
    try:
        with open(viewer_filepath, 'w', encoding="utf8") as file:
            file.write(str(soup))
        print("Modified HTML file written successfully")
    except Exception as e:
        print(f"Error writing modified HTML file: {str(e)}")
        return

    # Move the ixbrlviewer.js file
    viewer_js_path = os.path.join(viewer_outpath, 'ixbrlviewer.js')
    destination_js_path = 'app/static/js/ixbrlviewer.js'
    print(f"Moving {viewer_js_path} to {destination_js_path}")
    try:
        os.rename(viewer_js_path, destination_js_path)
        print("ixbrlviewer.js moved successfully")
    except Exception as e:
        print(f"Error moving ixbrlviewer.js: {str(e)}")

```


   This function does the following:
   a. Sets up the Arelle environment (lines 65-67)
   b. Runs Arelle's XBRL validation process (lines 68-69)
   c. Generates an HTML viewer for the XBRL document (lines 71-105)
   d. Moves the generated JavaScript file to the appropriate location (lines 107-115)

5. Arelle Command Line Interface:
   The code uses Arelle's command-line interface to process XBRL files. This is evident in the construction of the `args` variable:


```62:65:app/utils/xbrl_processing.py
    print('viewer path', viewer_filepath)
    args = f"--plugins={plugins} -f {output_file} --save-viewer {viewer_filepath} --viewer-url {viewer_url}"
    
    args = shlex.split(args)
```


6. Arelle Plugins:
   The code utilizes an Arelle plugin called "ixbrl-viewer" for creating an interactive XBRL viewer:


```59:60:app/utils/xbrl_processing.py
    plugins = os.path.join(ROOT, "dependencies", "ixbrl-viewer", "iXBRLViewerPlugin")
    viewer_url = "https://cdn.jsdelivr.net/npm/ixbrl-viewer@1.4.8/iXBRLViewerPlugin/viewer/dist/ixbrlviewer.js"
```


In summary, Arelle is used in this codebase as a powerful XBRL processing engine. It's integrated as a dependency, and its functionality is leveraged to validate XBRL documents, create interactive viewers, and process XBRL files through its command-line interface. The project extends Arelle's capabilities by using plugins and customizing the output for specific needs, such as creating an interactive XBRL viewer.

---

_**User**_



---

_**Assistant**_

Based on the provided code snippets, there isn't a specific file or code section that directly shows where concept labels are assigned. However, in typical XBRL processing using Arelle, concept labels are usually handled within the XBRL taxonomy files and processed by Arelle's core functionality.

That being said, the most relevant file for XBRL processing in the given codebase appears to be `app/utils/xbrl_processing.py`. While it doesn't explicitly show label assignment, it's using Arelle's functionality to process XBRL files.

If you need to work with concept labels specifically, you might want to look into:

1. The XBRL taxonomy files associated with your project, which define the concepts and their labels.

2. Arelle's internal processing of these taxonomies, which happens when you run the XBRL validation and viewer generation:

```python:app/utils/xbrl_processing.py
CntlrCmdLine.parseAndRun(args)
```

3. The generated viewer HTML and JavaScript, which likely contain the processed labels:

```python:app/utils/xbrl_processing.py
viewer_filepath = os.path.join(ROOT, viewer_outpath, 'viewer.html')
```

If you need to customize how labels are assigned or displayed, you might need to:

1. Extend Arelle's functionality by creating a custom plugin.
2. Modify the ixbrl-viewer plugin if it's not handling labels as desired.
3. Post-process the generated viewer HTML or JavaScript to adjust label display.

To find exactly where and how labels are being assigned, you may need to dive deeper into the Arelle codebase or the ixbrl-viewer plugin code, which are not fully visible in the provided snippets.

---

_**User**_



---

_**Assistant**_

Based on the code snippet you provided earlier, the `self._df['header']` is likely created or assigned in the `__init__` method of the `Table` class, which is the parent class of `StatementofActivities`. However, this method is not visible in the current file.

To find where `self._df['header']` is created or assigned, you should look for:

1. The `Table` class definition, which is likely in another file.
2. The `__init__` method of the `Table` class.
3. Any method in the `Table` class that processes the initial data and creates the DataFrame.

Here's a suggestion on how to find it:

1. Look for a file named something like `table.py` or `base_table.py` in your project directory.
2. In that file, find the `Table` class definition.
3. Look for the `__init__` method or any method that processes Excel data.

The code might look something like this:

```python:app/models/table.py
class Table:
    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        # ... other initialization code ...
        self._df = self._process_excel_data(excel_file, sheet_name)
        
    def _process_excel_data(self, excel_file, sheet_name):
        # Read Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        # Process the data
        # ...
        # Create the 'header' column
        df['header'] = ...  # This is where the 'header' column is likely created
        return df
```

If you can't find it in a separate `Table` class, it's possible that the `StatementofActivities` class is creating this column directly. In that case, look for any method in the `StatementofActivities` class that processes the Excel data, possibly called from the `__init__` method.

To locate this, you can search your project for:
1. Files that import pandas (look for `import pandas as pd`)
2. Methods that use `pd.read_excel()`
3. Any assignment to a DataFrame column named 'header'

If you still can't find it, it would be helpful to see more of your project structure and the full `Table` class definition if it exists.

---



---

