import { test } from '@antiwork/shortest'

// Specify file to test. City of Brea, CA
test('Click `Upload file(s)` button. Upload City of Brea, CA.xlsx located in `app/models/static/input_files/samples`')

// Test conversion new page
test('Once file is uploaded, verify new page loads opens after user clicks `Combine and convert file(s)` button. New page has 3 buttons, `Download file`, `Click to view in browser`, and `Convert Another ACFR`.')

// Test iXBRL viewer and new tab
test('Once conversion is complete and new page loads, verify iXBRL viewer works by clicking on `Click to view in browser` button. Verify it opens a new tab and loads the iXBRL viewer.')

// Test download file
test('Once conversion is complete and new page loads, verify `Download file` button works by clicking on it. Verify it downloads the file.')