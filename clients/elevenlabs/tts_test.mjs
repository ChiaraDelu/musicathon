import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';
import { writeFile } from 'fs/promises';
import 'dotenv/config';

const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

const audio = await elevenlabs.textToSpeech.convert(
  'JBFqnCBsd6RMkjVDRZzb', // voice_id (default voice)
  {
    text: 'The first move is what sets everything in motion.',
    modelId: 'eleven_multilingual_v2',
    outputFormat: 'mp3_44100_128',
  }
);

// Salva l'audio in un file invece di riprodurlo (più affidabile da terminale)
const chunks = [];
for await (const chunk of audio) {
  chunks.push(chunk);
}
await writeFile('output.mp3', Buffer.concat(chunks));

console.log('Audio salvato in output.mp3');
