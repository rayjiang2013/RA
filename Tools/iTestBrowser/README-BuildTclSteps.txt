
$BUILD_DIR> mkdir Wrappers
$BUILD_DIR> python extractWrappers.py   Paths hard-coded inside .py  ==> Wrapppers/*.fftc   (~232)

$BUILD_DIR> mkdir -p new_itest_actions/itest_params

$BUILD_DIR> sh createVarsHtml.sh
	SOURCE: * /Users/rcollazo/Downloads/RestAPITest/testcaselib.fftccat    (in .sh)      * This is new unzipped package - should contain this *.fftcaatt (catalog), NOTE: newest version appears to have changed formats.
	DEST:   ./itest_actions/itest_params/*.html                       (in .sh)


* getEval.sh  ->  extractWrapEval.py						> Wrappers/_getEval.txt			#	temporary - manually re-direct stdout, e.g. _getVal.txt
* getInjestData.sh  ->  extractWrapAndParamPerFile.py		> Wrappers/_getInjest.txt		#	temporary - ""    ""


mkdir $BUILD_DIR/Wrappers/NEW_api_pseudo-code
mkdir $BUILD_DIR/Wrappers/NEW_tc_pseudo-code

mkall  ->  maketcl.py -api
	SOURCE: wPath  = '$BUILD_DIR/Wrappers'      (from .py)
	DEST:   $BUILD_DIR/Wrappers/NEW_api_pseudo-code


mkdir $BUILD_DIR/Wrappers/NEW_api_pseudo-code_rest-links
mkdir $BUILD_DIR/Wrappers/NEW_api_pseudo-code_All-links
mkdir $BUILD_DIR/Wrappers/NEW_api_pseudo-code_html
mkdir $BUILD_DIR/Wrappers/HERO_test_params


sh tcl_rest_links.sh  ->  tcl_rest_links.py
	Required:	$PREPARED_DATA_LISTS/Rest_ALL-Links-XRef-Array.dat
	Required:	$PREPARED_DATA_LISTS/Rest_GET-Commands-XRef-Array.dat
	Required:	$PREPARED_DATA_LISTS/Rest_PUT-Commands-XRef-Array.dat
	Required:	$PREPARED_DATA_LISTS/Rest_POST-Commands-XRef-Array.dat
	Required:	$PREPARED_DATA_LISTS/Rest_DELETE-Commands-XRef-Array.dat
	SOURCE: $BUILD_DIR/Wrappers/NEW_api_pseudo-code
	DEST:   $BUILD_DIR/Wrappers/NEW_api_pseudo-code_rest-links


sh tcl_links.sh  ->  tcl_links.py
	SOURCE: $BUILD_DIR/Wrappers/NEW_api_pseudo-code_rest-links
	DEST:   $BUILD_DIR/Wrappers/NEW_api_pseudo-code_All-links


sh tcl2html.sh
	SOURCE:  $BUILD_DIR/Wrappers/NEW_api_pseudo-code_All-links
	DEST:    $BUILD_DIR/Wrappers/NEW_api_pseudo-code_html


sh merge_html.sh  ->  mergeHTML.py
	SOURCE_DIR_1:	$BUILD_DIR/Wrappers/itest_params_v1-KEEP
	SOURCE_DIR_2:	$BUILD_DIR/Wrappers/NEW_api_pseudo-code_html
	DEST:			$BUILD_DIR/Wrappers/HERO_test_params


cd $PV_RELEASE_DIR/AVNext-PV/RestAPITest/test_cases
sh extractActions    # DEST specified in sctipt (Scratch area: /work/itest/Analy/POSTED_062615/...)

Sources:
$PV_RELEASE_DIR/AVNext-PV/RestAPITest/test_cases:   (? include Utilities/)
extracts list for each to *.fftc, while maintaining, cloning  Dir hierarchy

$TEMP_DIR/POSTED_062615/
sh renameFiles  ==>  changes above to *.fftc.txt      (ToDo: merge functionality)

sh listContent.sh
	==>  creates above content with html formatting...  to *.fftc.html

Required:	$INSTALL_DIR/itest.html
Required:	$INSTALL_DIR/actions.html
Required:	$INSTALL_DIR/actions_alpha.html
Required:	$INSTALL_DIR/column2.html
Required:	$INSTALL_DIR/column3.html
