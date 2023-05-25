const token = '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'
function consigliami() {
    txt = document.getElementById('testo-consiglio')
    manga = document.getElementById("advice").value

    fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        },
        body: JSON.stringify({
            "model": "gpt-3.5-turbo",
            "messages": [{ "role": "user", "content": "mi consigleresti 5 manga simili a " + manga + ", vorrei che me li presentassi in un elenco puntato con anche una spiegazione del perche me li consigli, inoltre vorrei che ogni punto fosse formattato come una lista html" }]
        })
    }).then(response => {
        return response.json();

    }).then(data => {
        console.log(data.choices[0].message.content)
        txt.innerHTML = data.choices[0].message.content
    })
}
