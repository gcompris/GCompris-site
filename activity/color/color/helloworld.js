//set main namespace
goog.provide('helloworld');


//get requirements
goog.require('lime.Director');
goog.require('lime.Scene');
goog.require('lime.Sprite');
goog.require('lime.Layer');
goog.require('lime.Circle');
goog.require('lime.Label');
goog.require('lime.RoundedRect');
goog.require('lime.audio.Audio');
goog.require('lime.animation.Spawn');
goog.require('lime.animation.FadeTo');
goog.require('lime.animation.ScaleTo');
goog.require('lime.animation.MoveTo');
goog.require('lime.animation.Loop');
goog.require('lime.animation.RotateBy');
goog.require('lime.animation.Sequence');

var dataset;
var LOCALE = "en";
var output;
var selectedItem;
var imgBack;

var currentLevel;
var solutionIndex;
var solutionItem;
var questionItem;
var items;
var audioQuestion;
var audioIntro;
var readyScene;

function shuffle(array) {
  var tmp, current, top = array.length;

  if(top) while(--top) {
    current = Math.floor(Math.random() * (top + 1));
    tmp = array[current];
    array[current] = array[top];
    array[top] = tmp;
  }

  return array;
}

function getQuestion() {
    return ( currentLevel.questionText.replace(new RegExp("{text}"),
					       currentLevel.objects[solutionIndex].objectText) );
}

function nextQuestion(layer, level) {

    x = dataset.objectAreaXYWH[0];
    y = dataset.objectAreaXYWH[1];
    w = dataset.objectAreaXYWH[2];
    h = dataset.objectAreaXYWH[3];
    gap = 20;

    solutionIndex += 1;

    if ( solutionIndex >= items.length ) {
	displayLevel(layer, currentLevelIndex + 1);
	return;
   }

    questionItem.setText( getQuestion() )
	.setPosition(currentLevel.questionPosition[0],currentLevel.questionPosition[1])
	.setFontColor(dataset.questionColor).setFontSize(dataset.questionFont);
    solutionItem = items[solutionIndex];
    audioQuestion = new lime.audio.Audio(currentLevel.objects[solutionIndex].objectAudio);

    itemsShuffled = items.slice();
    itemsShuffled = shuffle(itemsShuffled);
    for (var i = 0; i < itemsShuffled.length; i++) {
	item = itemsShuffled[i]
	item.runAction(new lime.animation.MoveTo(x, y));
	x += item.getSize().width + gap;
	if ( x + item.getSize().width > dataset.objectAreaXYWH[0] + w ) {
	    x = dataset.objectAreaXYWH[0];
	    y += item.getSize().height + gap;
	}
    }
}

function placeObjects(layer, level) {

    output += " placeObjects ";

    x = dataset.objectAreaXYWH[0];
    y = dataset.objectAreaXYWH[1];
    w = dataset.objectAreaXYWH[2];
    h = dataset.objectAreaXYWH[3];
    gap = 20;

    audioQuestion = new lime.audio.Audio(currentLevel.objects[solutionIndex].objectAudio);

    items = new Array(level.objects.length);
    for (var i = 0; i < level.objects.length; i++) {
	item = new lime.Sprite()
	    .setFill(level.objects[i].objectImage)
	    .setAnchorPoint(0,0)
	    .setPosition(x,y);
	layer.appendChild(item);
	items[i] = item;

	if ( i == solutionIndex )
	    solutionItem = item;

        // item.runAction(new lime.animation.Loop(
	//     (new lime.animation.Sequence(
	// 	new lime.animation.RotateBy(5),
	// 	new lime.animation.RotateBy(-5)
	//     ))
	// ));

	//add some interaction
	goog.events.listen(item,['mousedown','touchstart'],function(e){

	    // Deselect previous item
	    if (selectedItem) {
		selectedItem.runAction(new lime.animation.ScaleTo(1));
	    }

	    // Move on top
	    layer.removeChild(e.targetObject);
	    layer.appendChild(e.targetObject);
            //animate
	    if ( e.targetObject != solutionItem ) {
		selectedItem = e.targetObject;
		e.targetObject.runAction(new lime.animation.ScaleTo(1.2));
	    } else {
		position = e.targetObject.getPosition();
		var anim = new lime.animation.Spawn(
		    new lime.animation.MoveTo(400, 220),
		    new lime.animation.ScaleTo(3)
		);
		e.targetObject.runAction(anim);
		goog.events.listen(anim,lime.animation.Event.STOP,function(){
		    var anim = new lime.animation.Spawn(
			new lime.animation.MoveTo(position),
			new lime.animation.ScaleTo(1)
		    );
		    e.targetObject.runAction(anim);
		    goog.events.listen(anim,lime.animation.Event.STOP,function(){
			nextQuestion(layer, level);
		    });
		})
		if ( audioQuestion.isPlaying() ) audioQuestion.stop();
		audioQuestion.play();
	    }
	});


	output += level.objects[i].objectImage + " xy=" + x + ' ' + y + '<br>';
	x += item.getSize().width + gap;
	if ( x + item.getSize().width > dataset.objectAreaXYWH[0] + w ) {
	    x = dataset.objectAreaXYWH[0];
	    y += item.getSize().height + gap;
	}
    }
}

function shuffleLevel(level) {
    for (var i = 0; i < level.objects.length; i++) {
	var randomnumber = Math.floor(Math.random() * level.objects.length)
	tmp = level.objects[randomnumber];
	level.objects[randomnumber] = level.objects[i];
	level.objects[i] = tmp;
    }
    return level;
}

function normalizeLevel(level) {
    for (var i = 0; i < level.objects.length; i++) {
	output+=' ' + i;
	level.objects[i].objectAudio = level.objects[i].objectAudio.replace(new RegExp("\\$LOCALE"),
					  LOCALE);
	level.objects[i].objectAudio = level.objects[i].objectAudio.replace(new RegExp("{text}"),
					  level.objects[i].objectText);
    }
    return level;
}

function clearLevel(layer) {
    if (! items )
	return;

    for (var i = 0; i < items.length; i++) {
	layer.removeChild(items[i]);

    }
}

function displayLevel(layer, levelIndex) {
    clearLevel(layer);
    currentLevelIndex = levelIndex
    imgBack.setFill(dataset.background).setAnchorPoint(0,0);

    output='<ul>';

    currentLevel = shuffleLevel(dataset.levels[levelIndex]);
    currentLevel = normalizeLevel(currentLevel);

    solutionIndex = 0;

    questionItem.setText( getQuestion() )
	.setPosition(currentLevel.questionPosition[0],currentLevel.questionPosition[1])
	.setFontColor(dataset.questionColor).setFontSize(dataset.questionFont);

    var loaded = 0;
    for (var i = 0; i < currentLevel.objects.length; i++) {
	preloadImage = new Image();
	output += "::" + i + " " + loaded + " ";
	preloadImage.onload = function()
	{
	    output += " loaded " + loaded;
	    loaded += 1;
	    if (loaded == currentLevel.objects.length - 1 ) {
		placeObjects(layer, currentLevel);
		//document.getElementById("result").innerHTML=output;
	    }
	}
	preloadImage.src = currentLevel.objects[i].objectImage;

    }

    output +='</ul>';
}

function loadLevel(layer, dataFile, imageType)
{
    var txtFile = new XMLHttpRequest();
    txtFile.open("GET", dataFile, true);
    txtFile.onreadystatechange = function() {
	if (txtFile.readyState === 4) {
	    if (txtFile.status === 200) {
		allText = txtFile.responseText;

		audio = document.createElement('audio');
		support = audio.canPlayType("audio/ogg; codecs=vorbis");
		if (support == "") {
		    allText = allText.replace(/.ogg/g, ".mp3");
		}

		if ( imageType != ".svg" ) {
		    allText = allText.replace(/.svg/g, imageType);
		}

		dataset = eval("("+allText+")");
		displayLevel(layer, 0);
	    }
	}
    }
    txtFile.send(null);
}

function createButton() {
    readyScene = new lime.Scene();
    var layer = new lime.Layer();
    var rectItem = new lime.RoundedRect().setRadius(7).setFill(200,200,200)
	.setAnchorPoint(.5,.5)
	.setPosition(400,200).setStroke(255,255,255,.2).setSize(240,60).setOpacity(0.8);
    buttonItem = new lime.Label().setFontSize(40).setText("I am Ready").setPosition(400,200);
    layer.appendChild(rectItem);
    layer.appendChild(buttonItem);
    readyScene.appendChild(layer);
    goog.events.listen(layer,['mousedown','touchstart'],function(e) {
	if ( audioIntro.isPlaying() ) audioIntro.stop();
	audioIntro.play();
	readyScene.getParent().popScene();
    });
    return readyScene;
}

// entrypoint
helloworld.start = function(imageType){

    audioIntro = new lime.audio.Audio("voices/en/intro/colors.ogg");

    var director = new lime.Director(document.body,800,520).setDisplayFPS(false);
    var scene = new lime.Scene();

    imgBack = new lime.Sprite()
    layer = new lime.Layer().setPosition(0,0);
    loadLevel(layer, "activity.desktop", imageType);
    layer.appendChild(imgBack);

    questionItem = new lime.Label();
    layer.appendChild(questionItem);

    scene.appendChild(layer);

    director.makeMobileWebAppCapable();

    startButtonScene = createButton();

    // set current scene active
    director.replaceScene(scene);
    director.pushScene(startButtonScene);
}


//this is required for outside access after code is compiled in ADVANCED_COMPILATIONS mode
goog.exportSymbol('helloworld.start', helloworld.start);
