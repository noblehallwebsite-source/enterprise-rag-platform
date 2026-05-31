import { NextRequest, NextResponse } from "next/server";

export async function POST(
    request: NextRequest
) {
    try {
        const formData =
            await request.formData();

        const response =
            await fetch(
                `${process.env.BACKEND_URL}/upload`,
                {
                    method: "POST",
                    headers: {
                        "x-api-key":
                            process.env.BACKEND_API_KEY!,
                    },
                    body: formData,
                }
            );

        const data =
            await response.json();

        return NextResponse.json(
            data,
            {
                status: response.status,
            }
        );
    } catch (error) {
        console.error(error);

        return NextResponse.json(
            {
                error:
                    "Upload failed",
            },
            {
                status: 500,
            }
        );
    }
}