echo "To show the coverage of specifc unit test case"
echo "To run it in eclipse, needs to edit $PATH in Environment of External Tools Configuration"
echo "current directory: $PWD"
coverage run --source $1 -m py.test -k $2
coverage report -m $2