const allowedMediaTypes = [
  "image/*",
  "video/*",
  "audio/*",
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.*",
  "text/plain",
  "text/csv",
];

const deniedExecutableTypes = [
  "application/vnd.microsoft.portable-executable",
  "application/x-msdownload",
  "application/x-msdos-program",
  "application/x-executable",
  "application/x-dosexec",
  "application/x-sh",
  "text/x-shellscript",
  "application/x-mach-binary",
];

const { URL } = require("url");

function getRedisConnection(env) {
  const redisURL = env("REDIS_URL");
  if (redisURL) {
    const parsed = new URL(redisURL);
    return {
      host: parsed.hostname,
      port: Number(parsed.portname) || 6379,
      password: parsed.password || undefined,
      db: 0,
    };
  }

  return {
    host: env("REDIS_HOST", "127.0.0.1"),
    port: env("REDIS_PORT", 6379),
    db: 0,
  };
}

module.exports = ({ env }) => ({
  "users-permissions": {
    config: {
      jwtManagement: "refresh",
      sessions: {
        httpOnly: true,
      },
    },
  },
  upload: {
    config: {
      security: {
        allowedTypes: allowedMediaTypes,
        deniedTypes: deniedExecutableTypes,
      },
    },
  },
  redis: {
    config: {
      connections: {
        default: {
          connection: getRedisConnection(env),
          settings: {
            debug: env.bool("REDIS_DEBUG", false),
          },
        },
      },
    },
  },
  "rest-cache": {
    enabled: env.bool("ENABLE_CACHE", true),
    config: {
      provider: {
        name: "redis",
        options: {
          ttl: 3600,
          connection: "default", // must match the connection defined above in the config.
        },
      },
      strategy: {
        contentTypes: ["api::article.article"],
        maxAge: 3600,
        debug: true, // turn off once confirmed its working
      },
    },
  },
});
