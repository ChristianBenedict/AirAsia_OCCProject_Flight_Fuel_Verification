// // untuk menampilkan nama file yang diupload dan memberikan validasi input file
// const fileInput = document.getElementById('file');
// const fileNamePlaceholder = document.getElementById('file-name-placeholder');

// fileInput.addEventListener('change', function() {
//     const fileName = fileInput.files[0].name;
//     fileNamePlaceholder.textContent = fileName;
// });

// const errorValidasiInput = document.getElementById('file');
// const fileError = document.getElementById('file-error');

// errorValidasiInput.addEventListener('invalid', function(event) {
//     event.preventDefault();
//     fileError.classList.remove('hidden');
// }, false);

// errorValidasiInput.addEventListener('change', function() {
//     if (errorValidasiInput.value) {
//         fileError.classList.add('hidden');
//     }
// }, false);
// //end validasi input file


// // Modal Confirmation add_data
// document.addEventListener('DOMContentLoaded', () => {
//     const uploadButton = document.getElementById('uploadButton');
//     const confirmationModal = document.getElementById('confirmationModal');
//     const modalFuelAgent = document.getElementById('modalFuelAgent');
//     const modalStartDate = document.getElementById('modalStartDate');
//     const modalEndDate = document.getElementById('modalEndDate');
//     const fileError = document.getElementById('file-error');
//     const fileInput = document.getElementById('file');
//     const startDateError = document.getElementById('start-date-error');
//     const endDateError = document.getElementById('end-date-error');
//     const form = document.getElementById('uploadDataForm');

//     uploadButton.addEventListener('click', (event) => {
//         event.preventDefault();

//         // Reset error messages
//         startDateError.classList.add('hidden');
//         endDateError.classList.add('hidden');
//         fileError.classList.add('hidden');

//         let isValid = true;

//         // Validasi input tanggal
//         const startDate = document.getElementById('date_of_data').value;
//         const endDate = document.getElementById('end_date_data').value;

//         if (!startDate) {
//             startDateError.classList.remove('hidden');
//             isValid = false;
//         }

//         if (!endDate) {
//             endDateError.classList.remove('hidden');
//             isValid = false;
//         }

//         // Validasi file
//         if (!fileInput.value) {
//             fileError.classList.remove('hidden');
//             isValid = false;
//         }

//         if (!isValid) {
//             return;
//         }

//         // Menampilkan nilai dalam modal
//         const fuelAgent = document.getElementById('vendor').value;
//         modalFuelAgent.textContent = fuelAgent;
//         modalStartDate.textContent = startDate;
//         modalEndDate.textContent = endDate;

//         confirmationModal.classList.remove('hidden'); // Menampilkan modal
//     });

//     document.getElementById('confirmButton').addEventListener('click', () => {
//         confirmationModal.classList.add('hidden');
//         // Submit form
//         form.submit();
//     });

//     document.getElementById('backButton').addEventListener('click', () => {
//         confirmationModal.classList.add('hidden');
//     });

//     fileInput.addEventListener('change', function() {
//         if (fileInput.value) {
//             fileError.classList.add('hidden');
//         }
//     });
// });
// // end Modal Confirmation add_data




// Modal Error add_data
const closeBtnError = document.querySelector('.close-btn-error');
const modalError = document.querySelector('.modal-error');
closeBtnError.addEventListener('click', () => {
  modalError.style.display = 'none';
});
// end Modal Error add_data

