MIT License. Do not use this abusively and be respectful of public servers acceptable
usage policies.

Based upon https://github.com/knrd1/chatgpt/tree/master with changes made by Chatgpt-4.

While the bot works, sometimes connecting is flaky, at which point the process needs to 
be killed and retried. It almost always works within 3 tries if it does not work at first.

Multiple bots have been tested in one room. I have seen them make a comment
about server load and then they talk to each other on how to improve server performance 
and then plan a trip to Rome. 

I plan on adding Kubernetes deployment functionality to the bot because who wouldn't love
having N number of assistant chatbots that can read server details running on your cluster?
