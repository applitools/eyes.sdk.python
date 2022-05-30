RESULT=0
MESSAGE=""
npm install
if [ $? -ne 0 ]; then
    ((RESULT+=1))
    MESSAGE+=$'\n npm install have failed'
    echo "${MESSAGE}"
fi
export UFG_ON_EG=true
npm run python:generate
if [ $? -ne 0 ]; then
    ((RESULT+=1))
    MESSAGE+=$'\n npm run python:generate have failed'
    echo "${MESSAGE}"
fi

# start eg client and save process id
# commented out if need eg client logs
export APPLITOOLS_SHOW_LOGS=true
npm run universal:eg &
EG_PID="$!"
export EXECUTION_GRID_URL=http://localhost:8080
echo $EXECUTION_GRID_URL

npm run python:run:parallel
if [ $? -ne 0 ]; then
    ((RESULT+=1))
    MESSAGE+=$'npm run python:run:parallel have failed'
    echo "${MESSAGE}"
fi

# Kill eg client by the process id
echo $EG_PID
kill $EG_PID

npm run python:report
if [ $? -ne 0 ]; then
    ((RESULT+=1))
    MESSAGE+=$'npm run python:report have failed'
    echo "${MESSAGE}"
fi
echo "RESULT = ${RESULT}"
echo "${MESSAGE}"
if [ $RESULT -eq 0 ]; then
    exit 0
else
    exit 1
fi
