let inputChanged = false;

$(document).ready(() => {
    loadExamplesList();
})
$('#dataset-selector').change(loadExamplesList);
$('#examples-select').change(loadExample);
$('#input-text').change(() => inputChanged = true);

$('#randomize-example').click(() => {
    const options = $("#examples-select option").map(function() {return $(this).val();}).get();
    const option = options[Math.floor(Math.random()*options.length)];
    $('#examples-select').val(option);
    loadExample();
});
$('#check-btn').click(checkText);

async function loadExamplesList() {
    const selectedDataset = $('#dataset-selector').val();
    const examples = await $.get(`/examples/${selectedDataset}`);
    for (const example of examples) {
        $('#examples-select').append(`<option value="${example}">${example}</option>`)
    }
    loadExample();
}

async function loadExample() {
    const selectedExample = $('#examples-select').val();
    const text = await getExample(selectedExample);
    $('#input-text').val(text);
    inputChanged = false;
}

async function getExample(exampleId) {
    const selectedDataset = $('#dataset-selector').val();
    return $.get(`/example/${selectedDataset}/${exampleId}`);
}

function getTotalScore(texts) {
    let maxScore = 0;
    for (const text of texts) {
        maxScore = Math.max(maxScore, text.score);
    }
    return maxScore;
}

async function checkText() {
    const similarTexts = await $.post('/analyze', {
        dataset: $('#dataset-selector').val(),
        method: $('#method-selector').val(),
        text: $('#input-text').val(),
        id: inputChanged ? '' : $('#examples-select').val()
    });
    const score = getTotalScore(similarTexts);
    $('#score-output').text((score * 100).toFixed(2) + '%');
    const threshold = parseInt($('#threshold-input').val(), 10) / 100;
    $('#score-label').text(score > threshold ? 'Plagiarism' : 'Not plagiarism');
    $('.similar-texts').empty();

    const addSimilarText = async () => {
        if (similarTexts.length === 0) {
            $('.similar-text .title').click(function () {
                $(this).parent().find('.text').toggleClass('d-none');
            });
            return;
        }
        const similar = similarTexts.pop();
        const text = await getExample(similar.example);
        $('.similar-texts').append(similarLayout(similar.score, similar.example, text, similar.score > threshold));
        setTimeout(addSimilarText, 0);
    }
    addSimilarText();
}


function similarLayout(score, exampleId, text, isPlagiarism) {
    const addClass = isPlagiarism? 'non-plagiarism' : 'plagiarism'
    return `<div class="similar-text ${addClass}">
        <div class="title"><span>${(score * 100).toFixed(2)}%</span>${exampleId}</div>
        <div class="text d-none">${text}</div>
</div>`
}