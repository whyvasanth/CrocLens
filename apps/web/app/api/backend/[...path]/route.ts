import { NextRequest, NextResponse } from "next/server";
import { getBackendBaseUrl, getSessionToken } from "../../auth/_shared";

const ALLOWED_METHODS = new Set(["GET", "POST", "PUT", "DELETE"]);

interface RouteContext {
  params: Promise<{
    path: string[];
  }>;
}

async function proxyBackend(request: NextRequest, context: RouteContext) {
  if (!ALLOWED_METHODS.has(request.method)) {
    return NextResponse.json({ detail: "Method not allowed." }, { status: 405 });
  }

  const { path } = await context.params;
  const backendPath = `/${path.join("/")}`;

  if (!backendPath.startsWith("/api/v1/")) {
    return NextResponse.json({ detail: "Only CrocLens API v1 routes can be proxied." }, { status: 400 });
  }

  const token = await getSessionToken();
  const query = request.nextUrl.search;
  const body = ["GET", "DELETE"].includes(request.method) ? undefined : await request.text();

  const backendResponse = await fetch(`${getBackendBaseUrl()}${backendPath}${query}`, {
    body: body || undefined,
    cache: "no-store",
    headers: {
      Accept: "application/json",
      ...(body ? { "Content-Type": request.headers.get("Content-Type") ?? "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    method: request.method
  });

  const payload = await backendResponse.text();
  return new NextResponse(payload, {
    headers: {
      "Content-Type": backendResponse.headers.get("Content-Type") ?? "application/json"
    },
    status: backendResponse.status
  });
}

export async function GET(request: NextRequest, context: RouteContext) {
  return proxyBackend(request, context);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxyBackend(request, context);
}

export async function PUT(request: NextRequest, context: RouteContext) {
  return proxyBackend(request, context);
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  return proxyBackend(request, context);
}
