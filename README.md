
runs out of context
leave work half finished
declare victory early

example of long running agent, my example of build error fix, it gets the logs if it fails
try to fix and build again until build is green.


context anxiety
    context fills up
    agent starts rushing
    declare done prematulely

poor self evaluation
    llm can not evaluate itself, it says it works fine even if the quality of work is not up to the mark.



Video why long running ai tasks lose continuity
repo as the system of record
long running agents lose context because context window is limited lets say 1000token, even if you expand it , it will be exhausted.
even if we summarize it will lose omething and every attempt to solve the same problem with different result. 

better to move memory to repo.
think of it as multiple agent working in a shift, each agent write what next agent needs. 

first node is progress file progress.md
##current state
commit 
Tests 32/45 passed
##completed
basic crud endpoints
##in progress
pagination [90%]
##known issue
##next steps
Fix pagination edge cases

second node is decision log decision.md  WHY
##decision: Use redis not the postgress
why: read on every API calls
Rejected:Postgres materialized view
Cost: too costly to maintain

third node is Git commit every change to git and see what changed in why

Agent.md

clock in
read progress.md
read decision.md
run make check
continuos from next step

clock out
update progress.md
run make check
commit completed work


