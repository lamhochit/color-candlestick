added as submodule:
==

under your project, run the following code to add submodule under `utils/message_hub` folder

`git submodule add git@gitlab.com:investbots/utilities/message_hub_py.git utils/message_hub`

---

if the file inside `utils/message_hub` is empty, run

`git submodule init`
`git submodule update`

---

to get update from `message_hub`

`cd utils/message_hub`
`git checkout master`
`git pull`

setup
==
`~/.aws/credentials`

```
[default]
aws_access_key_id = 
aws_secret_access_key =
```
ask Joshua/Frank for aws accessKeyId and secretAccessKey

*reference: https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/loading-node-credentials-shared.html*


testing
==
run `testing.js`
