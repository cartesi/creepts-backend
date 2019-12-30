if [ $# -eq 1 ]
then
    http get localhost:3001 content-type:application/json Instance=$1
else
    echo "Usage:./httpie_test_get_instance.sh <instance_number>"
fi
