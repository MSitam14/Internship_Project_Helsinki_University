document.querySelectorAll('button.deleteButton').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.id.replace('.pdb', '');
            if (confirm('Are you sure you want to delete this file?')) {
                fetch(`/api/files/${id}`, { method: 'DELETE' })
                    .then(response => {
                        if (response.status == 200) {
                            location.reload();
                        } else {
                            alert('Failed to delete the file.');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while deleting the file.');
                    });
            }
        });
    });