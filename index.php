<?php
$Destination['en'] = '-en';
$Destination['ar'] = '-ar';
$Destination['be'] = '-be';
$Destination['br'] = '-br';
// $Destination['bg'] = '-bg';
$Destination['ca'] = '-ca';
$Destination['cs'] = '-cs';
// $Destination['da'] = '-da';
$Destination['de'] = '-de';
$Destination['el'] = '-el';
$Destination['eo'] = '-eo';
$Destination['es'] = '-es';
$Destination['et'] = '-et';
$Destination['eu'] = '-eu';
$Destination['fi'] = '-fi';
$Destination['fr'] = '-fr';
$Destination['gd'] = '-gd';
$Destination['gl'] = '-gl';
$Destination['he'] = '-he';
$Destination['hr'] = '-hr';
$Destination['hu'] = '-hu';
$Destination['id'] = '-id';
$Destination['it'] = '-it';
$Destination['ko'] = '-ko';
$Destination['lt'] = '-lt';
// $Destination['lv'] = '-lv';
$Destination['mk'] = '-mk';
$Destination['ml'] = '-ml';
$Destination['nl'] = '-nl';
$Destination['nn'] = '-nn';
$Destination['pl'] = '-pl';
$Destination['pt'] = '-pt';
$Destination['pt-br'] = '-pt_BR';
$Destination['ro'] = '-ro';
$Destination['ru'] = '-ru';
$Destination['sk'] = '-sk';
$Destination['sl'] = '-sl';
$Destination['sq'] = '-sq';
// $Destination['sr'] = '-sr';
$Destination['sv'] = '-sv';
$Destination['sw'] = '-sw';
// $Destination['ta'] = '-ta';
$Destination['tr'] = '-tr';
// $Destination['th'] = '-th';
$Destination['uk'] = '-uk';
$Destination['zh-cn'] = '-zh_CN';
$Destination['zh-tw'] = '-zh_TW';

/*
  code copied from http://php.net/manual/en/function.http-negotiate-language.php
  determine which language out of an available set the user prefers most

  $available_languages        array with language-tag-strings (must be lowercase) that are available
  $http_accept_language    a HTTP_ACCEPT_LANGUAGE string (read from $_SERVER['HTTP_ACCEPT_LANGUAGE'] if left out)
*/
function prefered_language ($available_languages,$http_accept_language="auto") {
    // if $http_accept_language was left out, read it from the HTTP-Header
    if ($http_accept_language == "auto") $http_accept_language = isset($_SERVER['HTTP_ACCEPT_LANGUAGE']) ? $_SERVER['HTTP_ACCEPT_LANGUAGE'] : ''; 

    // standard  for HTTP_ACCEPT_LANGUAGE is defined under
    // http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
    // pattern to find is therefore something like this:
    //    1#( language-range [ ";" "q" "=" qvalue ] )
    // where:
    //    language-range  = ( ( 1*8ALPHA *( "-" 1*8ALPHA ) ) | "*" )
    //    qvalue         = ( "0" [ "." 0*3DIGIT ] )
    //            | ( "1" [ "." 0*3("0") ] )
    preg_match_all("/([[:alpha:]]{1,8})(-([[:alpha:]|-]{1,8}))?" .
                   "(\s*;\s*q\s*=\s*(1\.0{0,3}|0\.\d{0,3}))?\s*(,|$)/i",
                   $http_accept_language, $hits, PREG_SET_ORDER);

    // default language (in case of no hits) is the first in the array
    $bestlang = $available_languages[0];
    $bestqval = 0;

    foreach ($hits as $arr) {
        // read data from the array of this hit
        $langprefix = strtolower ($arr[1]);
        if (!empty($arr[3])) {
            $langrange = strtolower ($arr[3]);
            $language = $langprefix . "-" . $langrange;
        }
        else $language = $langprefix;
        $qvalue = 1.0;
        if (!empty($arr[5])) $qvalue = floatval($arr[5]);

        // find q-maximal language
        if (in_array($language,$available_languages) && ($qvalue > $bestqval)) {
            $bestlang = $language;
            $bestqval = $qvalue;
        }
        // if no direct hit, try the prefix only but decrease q-value by 10% (as http_negotiate_language does)
        else if (in_array($langprefix,$available_languages) && (($qvalue*0.9) > $bestqval)) {
            $bestlang = $langprefix;
            $bestqval = $qvalue*0.9;
        }
    }

    return $bestlang;
}

header("Location: index".$Destination[prefered_language(array_keys($Destination))].".html");
exit;

?>
