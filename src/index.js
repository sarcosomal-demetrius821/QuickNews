/**
 * Cloudflare Worker Router for QuickNews Django Container
 *
 * This Worker routes HTTP requests to the Django container running
 * in a Durable Object for SQLite persistence.
 */

import { Container, getRandom } from "@cloudflare/containers";

// Single instance for SQLite persistence
const INSTANCE_COUNT = 1;

export class DjangoContainerV2 extends Container {
  defaultPort = 8080;
  sleepAfter = "30m";
}

export default {
  async fetch(request, env) {
    try {
      // Get the single container instance (consistent for SQLite)
      const containerInstance = await getRandom(env.DJANGO_CONTAINER, INSTANCE_COUNT);

      // Forward all requests to the Django container
      return await containerInstance.fetch(request);
    } catch (error) {
      console.error('Worker error:', error);
      return new Response(
        JSON.stringify({
          error: 'Service Unavailable',
          message: error.message,
          timestamp: new Date().toISOString()
        }),
        {
          status: 503,
          headers: {
            'Content-Type': 'application/json',
            'Retry-After': '60'
          }
        }
      );
    }
  },

  async scheduled(event, env) {
    console.log('Scheduled cron trigger:', event.cron);
    try {
      const containerInstance = await getRandom(env.DJANGO_CONTAINER, INSTANCE_COUNT);
      const healthCheck = new Request('https://dummy.local/');
      await containerInstance.fetch(healthCheck);
      console.log('Keep-alive ping successful');
    } catch (error) {
      console.error('Scheduled keep-alive failed:', error);
    }
  }
};
