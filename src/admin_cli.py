#!/usr/bin/env python3
"""Admin CLI tool for platform management."""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Optional

import click
from sqlalchemy.ext.asyncio import AsyncSession

from .core.database import get_async_session
from .services.admin_service import AdminService
from .services.user_service import UserService
from .services.food_service import FoodService
from .services.exchange_service import ExchangeService


@click.group()
def cli():
    """Admin CLI for Neighborhood Food Sharing Platform."""
    pass


@cli.command()
@click.option('--days', default=7, help='Number of days for stats')
def stats(days: int):
    """Show platform statistics."""
    async def show_stats():
        async with get_async_session() as db:
            admin_service = AdminService(db)
            stats = await admin_service.get_platform_stats(days=days)
            
            click.echo(f"\n📊 Platform Statistics ({days} days)")
            click.echo("=" * 50)
            
            click.echo(f"👥 Users:")
            click.echo(f"   Total: {stats['users']['total']}")
            click.echo(f"   Active: {stats['users']['active']}")
            click.echo(f"   Activation Rate: {stats['users']['activation_rate']}%")
            
            click.echo(f"\n🏢 Buildings:")
            click.echo(f"   Total: {stats['buildings']['total']}")
            
            click.echo(f"\n🍲 Food Posts:")
            click.echo(f"   Total: {stats['food_posts']['total']}")
            click.echo(f"   Recent: {stats['food_posts']['recent']}")
            click.echo(f"   Active: {stats['food_posts']['active']}")
            
            click.echo(f"\n🤝 Exchanges:")
            click.echo(f"   Total: {stats['exchanges']['total']}")
            click.echo(f"   Completed (recent): {stats['exchanges']['completed_recent']}")
            click.echo(f"   Success Rate: {stats['exchanges']['success_rate']}%")
            
            click.echo(f"\n💰 Credits:")
            click.echo(f"   Total in circulation: {stats['credits']['total_in_circulation']}")
            click.echo(f"   Recent transactions: {stats['credits']['recent_transactions']}")
    
    asyncio.run(show_stats())


@cli.command()
def health():
    """Check system health."""
    async def check_health():
        async with get_async_session() as db:
            admin_service = AdminService(db)
            health_data = await admin_service.get_system_health()
            
            status_emoji = {
                'healthy': '✅',
                'degraded': '⚠️',
                'unhealthy': '❌'
            }
            
            click.echo(f"\n🔧 System Health Check")
            click.echo("=" * 30)
            
            emoji = status_emoji.get(health_data['status'], '❓')
            click.echo(f"Status: {emoji} {health_data['status'].upper()}")
            click.echo(f"Score: {health_data['score']}/100")
            click.echo(f"Database: {'✅ Connected' if health_data['database_connected'] else '❌ Disconnected'}")
            
            if health_data['issues']:
                click.echo(f"\n⚠️ Issues:")
                for issue in health_data['issues']:
                    click.echo(f"   • {issue}")
            else:
                click.echo(f"\n🎉 No issues detected!")
    
    asyncio.run(check_health())


@cli.command()
@click.option('--days', default=3, help='Days to look back for problematic exchanges')
def alerts(days: int):
    """Show problematic exchanges requiring attention."""
    async def show_alerts():
        async with get_async_session() as db:
            admin_service = AdminService(db)
            exchanges = await admin_service.get_problematic_exchanges(days=days)
            
            if not exchanges:
                click.echo(f"🎉 No problematic exchanges in the last {days} days!")
                return
            
            click.echo(f"\n🚨 Problematic Exchanges ({len(exchanges)} found)")
            click.echo("=" * 50)
            
            for exchange in exchanges:
                severity_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }
                
                emoji = severity_emoji.get(exchange['severity'], '❓')
                click.echo(f"\n{emoji} {exchange['description']}")
                click.echo(f"   Exchange ID: {exchange['id']}")
                click.echo(f"   Food: {exchange['food_title']}")
                click.echo(f"   Sharer: {exchange['sharer_name']}")
                click.echo(f"   Recipient: {exchange['recipient_name']}")
                click.echo(f"   Created: {exchange['created_at']}")
    
    asyncio.run(show_alerts())


@cli.command()
@click.argument('user_id')
def user(user_id: str):
    """Show detailed user activity."""
    async def show_user():
        async with get_async_session() as db:
            admin_service = AdminService(db)
            activity = await admin_service.get_user_activity(user_id)
            
            if not activity:
                click.echo(f"❌ User not found: {user_id}")
                return
            
            user_data = activity['user']
            credits = activity['credits']
            
            click.echo(f"\n👤 User Activity: {user_data['name']}")
            click.echo("=" * 50)
            
            click.echo(f"ID: {user_data['id']}")
            click.echo(f"Email: {user_data['email']}")
            click.echo(f"Phone: {user_data['phone']}")
            click.echo(f"Apartment: {user_data['apartment']}")
            click.echo(f"Building: {user_data['building']['name'] if user_data['building'] else 'None'}")
            click.echo(f"Verified: {'✅' if user_data['verified'] else '❌'}")
            click.echo(f"Created: {user_data['created_at']}")
            click.echo(f"Last Active: {user_data['last_active'] or 'Never'}")
            
            click.echo(f"\n💰 Credits:")
            click.echo(f"   Balance: {credits['balance']}")
            click.echo(f"   Lifetime Earned: {credits['lifetime_earned']}")
            click.echo(f"   Lifetime Spent: {credits['lifetime_spent']}")
            
            click.echo(f"\n📊 Activity:")
            click.echo(f"   Food Posts: {activity['activity']['food_posts_count']}")
            click.echo(f"   Exchanges as Sharer: {activity['activity']['exchanges_as_sharer']}")
            click.echo(f"   Exchanges as Recipient: {activity['activity']['exchanges_as_recipient']}")
            
            if activity['recent_food_posts']:
                click.echo(f"\n🍲 Recent Food Posts:")
                for post in activity['recent_food_posts'][:5]:
                    click.echo(f"   • {post['title']} ({post['status']}) - {post['created_at']}")
    
    asyncio.run(show_user())


@cli.command()
@click.argument('exchange_id')
@click.argument('action', type=click.Choice(['cancel', 'complete', 'reset']))
@click.argument('reason')
def exchange(exchange_id: str, action: str, reason: str):
    """Admin intervention on exchange."""
    async def handle_exchange():
        async with get_async_session() as db:
            exchange_service = ExchangeService(db)
            
            # Get exchange first to verify it exists
            exchange_obj = await exchange_service.get_exchange_by_id(exchange_id)
            if not exchange_obj:
                click.echo(f"❌ Exchange not found: {exchange_id}")
                return
            
            click.echo(f"🔧 {action.title()}ing exchange {exchange_id}")
            click.echo(f"Reason: {reason}")
            
            if not click.confirm("Are you sure?"):
                click.echo("Cancelled.")
                return
            
            success = False
            
            if action == 'cancel':
                success = await exchange_service.cancel_exchange(
                    exchange_id=exchange_id,
                    user_id="admin",
                    reason=f"Admin intervention: {reason}"
                )
            elif action == 'complete':
                success = await exchange_service.complete_exchange(
                    exchange_id=exchange_id,
                    user_id="admin",
                    rating=None,
                    notes=f"Admin intervention: {reason}"
                )
            elif action == 'reset':
                from ..models.exchange import ExchangeStatus
                exchange_obj.status = ExchangeStatus.PENDING
                exchange_obj.sharer_confirmed = False
                exchange_obj.recipient_confirmed = False
                exchange_obj.sharer_confirmed_at = None
                exchange_obj.recipient_confirmed_at = None
                success = True
            
            if success:
                await db.commit()
                click.echo(f"✅ Exchange {action}ed successfully!")
            else:
                click.echo(f"❌ Failed to {action} exchange")
    
    asyncio.run(handle_exchange())


@cli.command()
@click.option('--hours', default=24, help='Hours to look back for cleanup')
def cleanup(hours: int):
    """Clean up expired food posts and stale exchanges."""
    async def run_cleanup():
        async with get_async_session() as db:
            food_service = FoodService(db)
            
            click.echo(f"🧹 Running cleanup (last {hours} hours)")
            
            # Expire old posts
            expired_count = await food_service.expire_old_posts()
            click.echo(f"   ✅ Expired {expired_count} old food posts")
            
            await db.commit()
            click.echo("🎉 Cleanup completed!")
    
    asyncio.run(run_cleanup())


@cli.command()
@click.argument('building_id')
@click.option('--days', default=30, help='Number of days for stats')
def building(building_id: str, days: int):
    """Show building-specific statistics."""
    async def show_building():
        async with get_async_session() as db:
            admin_service = AdminService(db)
            stats = await admin_service.get_building_stats(building_id, days=days)
            
            if not stats:
                click.echo(f"❌ Building not found: {building_id}")
                return
            
            building_data = stats['building']
            
            click.echo(f"\n🏢 Building Statistics: {building_data['name']}")
            click.echo("=" * 50)
            
            click.echo(f"ID: {building_data['id']}")
            click.echo(f"Address: {building_data['address']}")
            
            click.echo(f"\n👥 Users ({days} days):")
            click.echo(f"   Total: {stats['users']['total']}")
            click.echo(f"   Active: {stats['users']['active']}")
            
            click.echo(f"\n📊 Activity ({days} days):")
            click.echo(f"   Food Posts: {stats['activity']['food_posts']}")
            click.echo(f"   Completed Exchanges: {stats['activity']['completed_exchanges']}")
            
            if stats['top_sharers']:
                click.echo(f"\n🌟 Top Sharers:")
                for sharer in stats['top_sharers']:
                    click.echo(f"   • {sharer['name']} (Apt {sharer['apartment']}): {sharer['posts_count']} posts")
    
    asyncio.run(show_building())


if __name__ == '__main__':
    cli()