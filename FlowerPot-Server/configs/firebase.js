const { initializeApp, applicationDefault, cert } = require('firebase-admin/app');
const { getFirestore, Timestamp, FieldValue } = require('firebase-admin/firestore');
const serviceAccount = require('./smart-flowerpot-3d998-firebase-adminsdk-gxz56-2567d74160.json');

initializeApp({
  credential: cert(serviceAccount)
});
const db = getFirestore();

// update docs
const updateFirebaseFlowerPot = async (flowerpot_data) => {
    try{
        const data = [
            {"light" : flowerpot_data[0]['light'], "moisture" : flowerpot_data[0]['moisture'], "updatedAt" : Timestamp.fromDate(new Date())}, 
            {"light" : flowerpot_data[1]['light'], "moisture" : flowerpot_data[1]['moisture'], "updatedAt" : Timestamp.fromDate(new Date())}, 
            {"light" : flowerpot_data[2]['light'], "moisture" : flowerpot_data[2]['moisture'], "updatedAt" : Timestamp.fromDate(new Date())}];

        const document = [
            db.collection("sensordata").doc(flowerpot_data[0]['name']),
            db.collection("sensordata").doc(flowerpot_data[1]['name']),
            db.collection("sensordata").doc(flowerpot_data[2]['name'])]

        await Promise.all([document[0].set(data[0]), document[1].set(data[1]), document[2].set(data[2])])
            .then(console.log('Firebase update complete'))
            .catch('Firebase update error')
    } catch(error) {
        console.log({ error })
    }
};

module.exports = {
    updateFirebaseFlowerPot,
}