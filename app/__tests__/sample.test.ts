import { test } from '@antiwork/shortest'


// Test conversion new page
test('Verify new page loads opens after user clicks `Combine and convert file(s)` button. New page has 3 buttons, `Download file`, `Click to view in browser`, and `Convert Another ACFR`.')

// Test notification messages
test('Verify notification messages are displayed correctly in top-left corner of screen during the conversion process, following user click of `Combine and convert file(s)` button. \
    Message displayed should be the following: `Initializing upload`, `Uploading files`, `Processing and validating files`, `Creating iXBRL file`, `Creating viewer`')