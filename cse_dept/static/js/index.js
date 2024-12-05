document.addEventListener('DOMContentLoaded', function() {
document.getElementById('lib_issue_id').addEventListener('keydown', function() {
    if (event.key === "Enter") {
        event.preventDefault();

        var id = this.value;
        console.log("fetching", id)

        fetch('/get_user_details/' + id)
            .then(response => response.json())
            .then(data => {
                // Update the fields with the returned data
                console.log(data)
                document.getElementById('name-field').innerHTML = 'User: ' + data.name;
                document.getElementById('id-field').innerHTML = 'ID: ' + data.id_number;
                document.getElementById('book-field').innerHTML = 'Books: '+data.issued_book;
                document.getElementById('fine-field').innerHTML = 'Fine: ' + data.fine;

                // Add similar lines for other fields
            });
    }
});
});