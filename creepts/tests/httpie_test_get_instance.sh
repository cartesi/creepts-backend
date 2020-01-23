if [ $# -eq 1 ]
then
    echo "{\"Instance\":$1}" | http get localhost:3001 content-type:application/json
else
    echo "Usage:./httpie_test_get_instance.sh <instance_number>"
fi
