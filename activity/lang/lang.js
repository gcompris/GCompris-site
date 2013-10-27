/* gcompris - gcompris.c
 *
 * Copyright (C) 2000, 2013 Bruno Coudoin
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, see <http://www.gnu.org/licenses/>.
 */
var dataSet;
var currentRefreshFunction;
var currentChapter;
var currentLesson;

var currentQuestionId;
var currentExerciseType;

function playerInit(triplets) {
    var source = '';
    for (var i = 0; i < triplets.length; i++) {
	var sound = triplets[i].voice;
	var baseSound = sound.substring(sound.lastIndexOf('/')+1, sound.lastIndexOf('.'));
        source += '<audio id="' + baseSound + '" preload="auto">';
        source +=  '<source id="audio_player_ogg" src="' + sound + '"  type="audio/ogg" />';
	// Replace voices/fr/intro/xx.ogg in voices.mp3/fr/intro/xx.mp3
	mp3 = sound.substring(0, sound.lastIndexOf('.')) + '.mp3';
	mp3 = "voices.mp3" + mp3.substring(mp3.indexOf('/'));
        source +=  '<source id="audio_player_mp3" src="' + mp3 + '" type="audio/mpeg" />';
        source += '</audio>';
    }
    $('#divAudioPlayer').html(source);
}

function play(sound) {
    var baseSound = sound.substring(sound.lastIndexOf('/')+1, sound.lastIndexOf('.'));
    var audio = $('#' + baseSound).get(0);
    audio.play();
}

function playIntro(sound) {
    var source = '<audio id="audio_player">';
    source +=  '<source id="audio_player_ogg" src="' + sound + '" type="audio/ogg" />';
    // Replace voices/fr/intro/xx.ogg in voices.mp3/fr/intro/xx.mp3
    mp3 = sound.substring(0, sound.lastIndexOf('.')) + '.mp3';
    mp3 = "voices.mp3" + mp3.substring(mp3.indexOf('/'));
    source +=  '<source id="audio_player_mp3" src="' + mp3 + '" type="audio/mpeg" />';
    source +=  '</audio>';

    $('#divAudioPlayerIntro').html(source);

    var audio = $('#audio_player').get(0);
    audio.play();
}

window.onload = function() {
    $(document).ready(function(){
	window.onresize = function() {
	    currentRefreshFunction();
	}
        $('#exit').on('click', function (e) {
	    window.location.href = "http://gcompris.net";
        });
        $('#home').on('click', function (e) {
            displayMenu();
        });
        $('#config').on('click', function (e) {
            displayConfig();
        });
        $('#help').on('click', function (e) {
            displayHelp();
        });
        $('#level-down').on('click', function (e) {
	    currentLesson--;
	    if (currentLesson < 0) {
		currentLesson = dataSet.chapters[currentChapter].lessons.length - 1;
	    }
            displayLesson(currentChapter, currentLesson);
        });
        $('#level-up').on('click', function (e) {
	    currentLesson++;
	    if (currentLesson >= dataSet.chapters[currentChapter].lessons.length) {
		currentLesson = 0;
	    }
            displayLesson(currentChapter, currentLesson);
        });
        $('#repeat').on('click', function (e) {
	    var audio = $('#audio_player').get(0);
	    audio.play();
        });
    });
};

function refreshBar()
{
    w = $('#bar').width();
    h = $('#bar').height();
    document.getElementById("bar").style.top = Math.floor($(window).height() - h) + "px";
    document.getElementById("bar").style.left = Math.floor($(window).width() / 2 - w / 2) + "px";
    buttonWidth = Math.floor(Math.min($(window).width()/10, 68));
    $('.gcBarButton').css('height', buttonWidth);
    fontSize = Math.floor(Math.min($(window).width()/16, 34));
    $('.level').css('font-size', fontSize);
}

function updateLevel()
{
    document.getElementById("level").innerHTML =
	currentLesson + 1 + "/" + dataSet.chapters[currentChapter].lessons.length;
}

function getLayout()
{
    barHeight = $('#bar').height() + 50;
    pos = { 'x': [], 'y': []};
    if ( $(window).width() > $(window).height() ) {
	// Horizontal layout (1x4)
	imgSize = Math.floor($(window).width() / 7);
	pos['x'][0] = Math.floor($(window).width() * (1 / 5) - imgSize / 2);
	pos['x'][1] = Math.floor($(window).width() * (2 / 5) - imgSize / 2);
	pos['x'][2] = Math.floor($(window).width() * (3 / 5) - imgSize / 2);
	pos['x'][3] = Math.floor($(window).width() * (4 / 5) - imgSize / 2);
	pos['y'][0] = Math.floor(($(window).height() - barHeight)/ 2 - imgSize / 2);
	pos['y'][1] = pos['y'][0];
	pos['y'][2] = pos['y'][0];
	pos['y'][3] = pos['y'][0];
    } else {
	// Vertical layout (2x2)
	imgSize = Math.floor($(window).width() / 4);
	pos['x'][0] = Math.floor($(window).width() * (1 / 4) - imgSize / 2);
	pos['x'][1] = Math.floor($(window).width() * (3 / 4) - imgSize / 2);
	pos['x'][2] = pos['x'][0];
	pos['x'][3] = pos['x'][1];
	pos['y'][0] = Math.floor(($(window).height() - barHeight - 40) * ( 1 / 4 ) - imgSize / 2 + 40);
	pos['y'][1] = pos['y'][0];
	pos['y'][2] = Math.floor(($(window).height() - barHeight - 40) * ( 3 / 4 ) - imgSize / 2 + 40);
	pos['y'][3] = pos['y'][2];
    }
    return pos;
}

function displayConfig()
{
    currentRefreshFunction = displayConfig;
    $('#home').show();
    $('#repeat').hide();
    $('#levelGroup').hide();
    refreshBar();

    content = '<div class="container">';
    content += '  <div class="row">';
    for (var i = 0; i < dataSet.locales.length ; i++) {
	content += '    <div class="col-xs-12" style="margin-top: 10px">';
        content += '      <a href="index.html?locale=' + dataSet.locales[i].code + '" class="btn btn-primary" style="display: block; margin: 0 auto;">';
        content += '        <h2 class="langtitle">' + dataSet.locales[i].name + '</h2>';
        content += '      </a>';
        content += '    </div>';
    }
    content += '  </div>';
    content += '</div>';
    document.getElementById("divGameArea").innerHTML = content;
}

function displayHelp()
{
    $('#home').show();
    $('#repeat').hide();
    $('#levelGroup').hide();
    refreshBar();

    result =  '<div class="centerBg">';
    result += '  <h2 class="langtitle">' + dataSet.strings.help + '</h2>';
    result += '</div>';
    result += '<button id="helpOk" class="btn btn-primary gcbutton" style="margin-left: 50%;">';
    result += '  <img src="ok.png" style="width: 80px; margin: 0 auto;"/>';
    result += '</button>';

    $('#divGameArea').hide();
    $('#divHelpArea').show();
    document.getElementById("divHelpArea").innerHTML = result;

    $('#helpOk').on('click', function (e) {
	$('#divHelpArea').hide();
	$('#divGameArea').show();
    });

    playIntro("voices/" + locale + "/intro/lang-nature.ogg");
}

function displayMenu()
{
    currentRefreshFunction = displayMenu;
    $('#home').show();
    $('#repeat').hide();
    $('#levelGroup').hide();
    refreshBar();

    currentChapter = -1;
    currentLesson = -1;
    currentExerciseType = -1;
    refreshBar();
    pos = getLayout();
    questions = [
	{'image': 'lang-object.png', 'description': dataSet.chapters[0].name},
	{'image': 'lang-other.png', 'description': dataSet.chapters[1].name},
	{'image': 'lang-nature.png', 'description': dataSet.chapters[2].name},
	{'image': 'lang-people.png', 'description': dataSet.chapters[3].name}
    ];
    content = '';
    for (var i = 0; i < questions.length ; i++) {
        posstr = 'position: absolute; top: ' + pos['y'][i] + 'px; left: ' + pos['x'][i] + 'px;';
        content += '    <div style="' + posstr + '">';
        content += '      <button id="choice' + i + '" chapter=' + i + ' class="btn btn-primary">';
	content += '        <img src="' + questions[i].image + '" style="width: ' + imgSize + 'px; height: '+ imgSize + 'px; margin: 0 auto"/>';
        content += '        <div style="width: ' + imgSize + 'px;"><h2 class="langtitle">' + questions[i].description + '</h2></div>';
        content += '      </button>';
        content += '    </div>';
    }
    document.getElementById("divGameArea").innerHTML = content;

    for (var i = 0; i < 4; i++) {
        $('#choice' + i).on('click', function (e) {
            currentChapter = $(this).attr("chapter")
            displayLesson(currentChapter, 0);
        });
    }

}

function getCarousel(triplets, category)
{
    barHeight = $('#bar').height();
    imgSize = Math.floor(Math.min($(window).height(), $(window).width()) / 2);

    result = '<div class="centerBg">';
    result += '<h2 class="langtitle">' + category + '</h2>';
    result += '</div>';

    result += '<div>';
    result += '<img id="carouselImg" onload="carouselImageLoaded()" src="' + triplets[0].image
	+ '" style="display: block; margin: 0 auto; width: '
	+ imgSize + 'px; height ' + imgSize + 'px;"/>';
    result += '</div>';

    fontSize = Math.floor(Math.min($(window).width()/16, 55));
    result += '<div>';
    result += '  <div style="display: inline-block; width: 9%;">';
    result += '    <img id="carouselLeft" src="prev.png" class="gcbutton" style="float: right;"/>';
    result += '  </div>';
    result += '  <div class="centerBg" style="display: inline-block; width: 80%; text-align: center;">';
    result += '    <h1 id="carouselTxt" class="langtitle" style="display: inline-block; font-size:' + fontSize + 'px;"></h1>';
    result += '  </div>';
    result += '  <div style="display: inline-block; width: 9%;">';
    result += '    <img id="carouselRight" src="next.png" class="gcbutton" style="float: left;"/>';
    result += '  </div>';
    result += '</div>';

    img2Size = 64;
    pos = 'position: absolute; top: ' + 50
	+ 'px; left: ' + Math.floor($(window).width() / 2 - img2Size / 2) + 'px;';
    result += '<img id="goToExercice" src="play.png" class="gcbutton" style="width: '
	+ img2Size + 'px; ' + pos + '"'
	+ ' data-toggle="tooltip" data-placement="right" title="Run the Quiz">'
	+ '</img>';

    return result;
}

function displayCurrentLesson() {
    displayLesson(currentChapter, currentLesson);
}

function carouselImageLoaded()
{
    triplet = dataSet.chapters[currentChapter].lessons[currentLesson].triplets[currentQuestionId];
    document.getElementById("carouselTxt").innerHTML = triplet.description;
    play(triplet.voice);
}

var currentCarouselPassed;
function updateCarousel(triplet) {
    $('#carouselImg').attr('src', triplet.image);

    currentCarouselPassed[currentQuestionId] = true;
    allSet = true;
    for (var i = 0; i < dataSet.chapters[currentChapter].lessons[currentLesson].triplets.length; i++) {
	if (currentCarouselPassed[i] == false) {
	    allSet = false;
	    break;
	}
    }
    if ( allSet ) $('#goToExercice').show();
}

function displayLesson(chapter, lesson) {
    currentRefreshFunction = displayCurrentLesson;
    $('#home').show();
    $('#repeat').show();
    $('#levelGroup').show();
    refreshBar();
    playerInit(dataSet.chapters[chapter].lessons[lesson].triplets);

    currentChapter = chapter;
    currentLesson = lesson;
    currentQuestionId = 0;
    currentExerciseType = -1;

    currentCarouselPassed = [];
    for (var i = 0; i < dataSet.chapters[chapter].lessons[lesson].triplets.length; i++) {
	currentCarouselPassed[i] = false;
    }

    updateLevel();
    refreshBar();
    document.getElementById("divGameArea").innerHTML =
	getCarousel(dataSet.chapters[chapter].lessons[lesson].triplets,
		    dataSet.chapters[chapter].lessons[lesson].name);
    updateCarousel(dataSet.chapters[chapter].lessons[lesson].triplets[currentQuestionId]);

    $('#goToExercice').hide();

    $('#goToExercice').on('click', function (e) {
        displayExercise(currentChapter, currentLesson, 0, 0);
    });

    $('#carouselLeft').on('click', function () {
        triplets = dataSet.chapters[chapter].lessons[lesson].triplets;
        currentQuestionId--;
	if ( currentQuestionId < 0 )
	    currentQuestionId = triplets.length - 1;
	updateCarousel(triplets[currentQuestionId]);
    })

    $('#carouselRight').on('click', function () {
        triplets = dataSet.chapters[chapter].lessons[lesson].triplets;
        currentQuestionId++;
	if ( currentQuestionId >= triplets.length )
	    currentQuestionId = 0;
	updateCarousel(triplets[currentQuestionId]);
    })

}

function displayCurrentExercise() {
    displayExercise(currentChapter, currentLesson,
		    currentQuestionId, currentExerciseType);
}

function displayExercise(chapter, lesson, questionId, exerciseType) {
    currentRefreshFunction = displayCurrentExercise;
    $('#home').show();
    $('#repeat').show();
    $('#levelGroup').show();
    refreshBar();

    currentQuestionId = questionId;
    currentExerciseType = exerciseType;
    triplets = dataSet.chapters[chapter].lessons[lesson].triplets;
    play(triplets[questionId].voice);
    questionsId = [ questionId ];

    // Search 3 more tiplets randomly
    while (questionsId.length != 4) {
        rand = Math.floor(Math.random() * triplets.length);
        if ( $.inArray(rand, questionsId) == -1 ) {
            questionsId.push( rand );
        }
    }
    questions = [];
    for (var i = 0; i < 4; i++) {
        questions[i] = dataSet.chapters[chapter].lessons[lesson].triplets[questionsId[i]];
    }
    // Shuffle
    for (var i = 0; i < 4; i++) {
        rand = Math.floor(Math.random() * 4);
        tmp = questions[i];
        questions[i] = questions[rand];
        questions[rand] = tmp;
    }
    content = '';
    fontSize = Math.floor(Math.min($(window).width()/16, 55));
    if (exerciseType == 0) {
	content += '  <div class="centerBg">';
        content += '<h1 class="langtitle" style="font-size: ' + fontSize + 'px";>' + dataSet.chapters[chapter].lessons[lesson].triplets[questionId].description + '</h1>';
        content += '  </div>';
    }

    pos = getLayout();
    for (var i = 0; i < 4; i++) {
        posstr = 'position: absolute; top: ' + pos['y'][i] + 'px; left: ' + pos['x'][i] + 'px;';
        content += '    <div style="' + posstr + '">';
        content += '      <button id="choice' + i + '" description="' + questions[i].description + '" class="btn btn-primary">';
	content += '        <img src="' + questions[i].image + '" style="width: ' + imgSize + 'px; height: '+ imgSize + 'px; margin: 0 auto"/>';
	if (exerciseType < 2) {
	    content += '        <div class="center" style="width: ' + imgSize + 'px;"><h2 class="langtitle">' + questions[i].description + '</h2></div>';
	}
        content += '      </button>';
        content += '    </div>';
    }
    document.getElementById("divGameArea").innerHTML = content;

    for (var i = 0; i < 4; i++) {
        $('#choice' + i).on('click', function (e) {
            triplets = dataSet.chapters[chapter].lessons[lesson].triplets;
            x = triplets[questionId].description;
            if (dataSet.chapters[chapter].lessons[lesson].triplets[questionId].description === $(this).attr("description")) {
                currentQuestionId++;
                if (currentQuestionId < triplets.length ) {
                    displayExercise(currentChapter, currentLesson, currentQuestionId, currentExerciseType);
                } else {
		    currentExerciseType++;
		    if (currentExerciseType < 3) {
                        displayExercise(currentChapter, currentLesson, 0, currentExerciseType);
		    } else {
                        displayLesson(currentChapter, currentLesson + 1);
		    }
                }
            }
        });
    }
}

function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}

locale = getURLParameter('locale');
if ( ! locale ) {
    locale = 'en';
}
$.getJSON( "words-" + locale + ".json", function( data ) {
    dataSet = data;
    displayMenu();
});

