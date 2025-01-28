
const postgreService = require('./postgresqlService.js');
const { Pool } = require('pg');

async function testGetBookCoverUrl() {

    const bookId = 16586;
    const isbn = '9781408855911';       //Harry Potter Prisonnier d'askaban

    // const bookId = 37941;
    // const isbn = '9780439358071';

    // const bookId = 38040;
    // const isbn = '9780439655484';


    // const isbn = '765354950';
    // const bookId = 3;
    // const isbn = null;
    // const bookId = 2;
    // const isbn = '1595542329';
    // const bookId = 1;
    // const isbn = '1416950419';
    

    try {
        const coverUrl = await postgreService.getBookCoverUrl(bookId, isbn);
        const bookdata = await postgreService.getBookDataBdd(bookId);
        console.log('Cover URL:', coverUrl);
        console.log("bookdata:",bookdata)
    } catch (error) {
        console.error('Error:', error);
    }
}

testGetBookCoverUrl();
